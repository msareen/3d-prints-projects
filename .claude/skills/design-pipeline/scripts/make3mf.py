#!/usr/bin/env python3
"""make3mf.py: pack checked STL parts into one 3MF file (3MF Core spec, millimetres).

Each STL becomes one named object with its own display colour (from the part's
JSON metadata `preview_color`, if any), placed exactly where the build put it.
Slicers (PrusaSlicer, Bambu Studio, OrcaSlicer, Cura) open it as one project
with separate objects, which keeps multi-part and multi-colour designs together.

    python -P make3mf.py out.3mf part-a.stl part-b.stl --title "wall hook"
    python -P make3mf.py out.3mf a.stl b.stl c.stl --bed 180x180x180 --plate a --plate b,c

With --plate (repeatable, comma-separated STL stems), each plate's parts are centred
on their own bed in Bambu Studio's plate grid and the plate list is written to
Metadata/model_settings.config. STLs not named in any --plate are left out. Bambu
Studio applies the plate list only if the 3MF also has a project config
(Metadata/project_settings.config); without one it loads the geometry onto a single
plate. So the plate file also gets the printer, process and filament presets from the
Bambu Lab profiles installed with Bambu Studio (bambu.py; --nozzle, --layer, --material,
--printer, and a bed with its height, --bed 180x180x180). If no installed profile
matches, the 3MF is written without one and a warning says Bambu Studio will show one
plate. Other slicers ignore both files and show the parts spread over the plate grid.
A top view of the plates, <out>-plates.svg, is written next to the 3MF.

Run with the 3d-print-design venv interpreter (needs trimesh to read STL).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import numpy as np
import shapely
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bambu  # noqa: E402

CONTENT_TYPES = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
 <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
 <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
</Types>
"""
RELS = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
 <Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>
</Relationships>
"""
HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


def _num(x: float) -> str:
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# Bambu Studio / OrcaSlicer read Metadata/model_settings.config (the plate list) only from
# files whose Application starts with "BambuStudio-" AND that carry a project config;
# otherwise they load geometry only. bambu.project_config() gives the version to use.
BBL_APPLICATION = "BambuStudio-02.00.00.00"
PLATE_GAP = 1.0 / 5.0          # Bambu's LOGICAL_PART_PLATE_GAP: plates are laid out bed * 1.2 apart


def plate_origin(index: int, count: int, bed) -> tuple[float, float]:
    """Front-left corner of plate `index` in Bambu Studio's plate grid (PartPlateList)."""
    root = count ** 0.5
    cols = int(round(root)) + (1 if root > round(root) else 0)
    cols = max(cols, 1)
    row, col = divmod(index, cols)
    return col * bed[0] * (1 + PLATE_GAP), -row * bed[1] * (1 + PLATE_GAP)


def model_settings_xml(plates) -> str:
    """plates: list of (plate name, [object ids])."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n<config>\n']
    for i, (pname, oids) in enumerate(plates):
        out.append("  <plate>\n"
                   f'    <metadata key="plater_id" value="{i + 1}"/>\n'
                   f"    <metadata key=\"plater_name\" value={quoteattr(pname)}/>\n"
                   '    <metadata key="locked" value="false"/>\n')
        for oid in oids:
            out.append("    <model_instance>\n"
                       f'      <metadata key="object_id" value="{oid}"/>\n'
                       '      <metadata key="instance_id" value="0"/>\n'
                       "    </model_instance>\n")
        out.append("  </plate>\n")
    out.append("</config>\n")
    return "".join(out)


def model_xml(parts, title: str, application: str = "design-pipeline (Claude Code skill)") -> str:
    """parts: list of (name, vertices (n,3), faces (m,3), colour '#rrggbb' or None)."""
    bbl = application.startswith("BambuStudio-")
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n'
           '<model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02"'
           + (' xmlns:BambuStudio="http://schemas.bambulab.com/package/2021"' if bbl else "") + '>\n',
           f' <metadata name="Title">{escape(title)}</metadata>\n',
           f' <metadata name="Application">{escape(application)}</metadata>\n',
           *([' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'] if bbl else []),
           ' <metadata name="Generator">design-pipeline (Claude Code skill)</metadata>\n',
           " <resources>\n  <basematerials id=\"1\">\n"]
    for name, _, _, color in parts:
        col = (color if color and HEX.fullmatch(color) else "#B0B0B0").upper() + "FF"
        out.append(f"   <base name={quoteattr(name)} displaycolor=\"{col}\"/>\n")
    out.append("  </basematerials>\n")
    for i, (name, verts, faces, _) in enumerate(parts):
        oid = i + 2
        out.append(f'  <object id="{oid}" type="model" name={quoteattr(name)} pid="1" pindex="{i}">\n'
                   "   <mesh>\n    <vertices>\n")
        out.extend(f'     <vertex x="{_num(x)}" y="{_num(y)}" z="{_num(z)}"/>\n' for x, y, z in verts)
        out.append("    </vertices>\n    <triangles>\n")
        out.extend(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>\n' for a, b, c in faces)
        out.append("    </triangles>\n   </mesh>\n  </object>\n")
    out.append(" </resources>\n <build>\n")
    out.extend(f'  <item objectid="{i + 2}"/>\n' for i in range(len(parts)))
    out.append(" </build>\n</model>\n")
    return "".join(out)


def write_3mf(path: Path, stl_paths, title: str, bed=None, copies: int = 1, gap: float = 10.0,
              plates=None, presets: dict | None = None) -> dict:
    """bed = (x, y): move all parts together so their footprint is centred on the bed.

    copies > 1 places that many copies of the part set side by side along X (gap mm apart),
    each as its own named object (<part>-1, <part>-2, ...).

    The parts keep their positions relative to each other; Z is untouched (they sit on Z = 0).
    """
    parts = []
    summary = []
    for stl in stl_paths:
        stl = Path(stl)
        mesh = trimesh.load(str(stl), file_type="stl", force="mesh")
        if not mesh.is_watertight:
            raise ValueError(f"{stl.name} is not watertight; refusing to package it")
        meta_path = stl.with_suffix(".json")
        color = None
        if meta_path.is_file():
            color = json.loads(meta_path.read_text(encoding="utf-8")).get("preview_color")
        verts = np.asarray(mesh.vertices, dtype=np.float64)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        parts.append((stl.stem, verts, faces, color))
        summary.append({"name": stl.stem, "vertices": len(verts), "triangles": len(faces),
                        "volume_mm3": round(float(mesh.volume), 2)})
    if not parts:
        raise ValueError("no STL files given")
    if plates:
        return _write_plates(path, parts, summary, title, bed, plates, presets or {})
    if copies > 1:
        # lay out `copies` copies of the whole part set side by side along X, gap mm apart
        allv = np.vstack([p[1] for p in parts])
        step = float(allv[:, 0].max() - allv[:, 0].min()) + gap
        parts = [(f"{n}-{k + 1}", v + np.array([k * step, 0.0, 0.0]), f, c)
                 for k in range(copies) for n, v, f, c in parts]
        summary = [{**s, "copies": copies} for s in summary]
    if bed:
        allv = np.vstack([p[1] for p in parts])
        lo, hi = allv.min(0), allv.max(0)
        shift = np.array([bed[0] / 2 - (lo[0] + hi[0]) / 2, bed[1] / 2 - (lo[1] + hi[1]) / 2, 0.0])
        parts = [(n, v + shift, f, c) for n, v, f, c in parts]
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("3D/3dmodel.model", model_xml(parts, title))
    tmp.replace(path)
    return {"file": path.name, "objects": summary}


def footprint(verts: np.ndarray, faces: np.ndarray):
    """Top view of a closed mesh (shapely): the union of its upward-facing triangles."""
    tri = verts[faces]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    tri = tri[n[:, 2] > 1e-9][:, :, :2]
    polys = shapely.polygons(np.concatenate([tri, tri[:, :1]], axis=1))
    polys = polys[shapely.area(polys) > 1e-9]
    return shapely.union_all(shapely.buffer(polys, 0.01)).buffer(-0.01).simplify(0.05)


def _svg_path(geom, X, Y) -> str:
    d = []
    for poly in getattr(geom, "geoms", [geom]):
        if poly.is_empty or poly.geom_type != "Polygon":
            continue
        for ring in [poly.exterior, *poly.interiors]:
            d.append("M" + " L".join(f"{X(x):.2f},{Y(y):.2f}" for x, y in np.asarray(ring.coords)) + " Z")
    return " ".join(d)


def plates_svg(placed, plates, bed, title: str, note: str = "") -> str:
    """Top view of every plate where Bambu Studio puts it: bed squares in its plate grid, parts filled."""
    s, pad, head, foot = 1.6, 30.0, 70.0, 56.0
    origins = [plate_origin(i, len(plates), bed) for i in range(len(plates))]
    x0 = min(o[0] for o in origins)
    x1 = max(o[0] for o in origins) + bed[0]
    y0 = min(o[1] for o in origins)
    y1 = max(o[1] for o in origins) + bed[1]
    W, H = (x1 - x0) * s + 2 * pad, (y1 - y0) * s + 2 * pad + head + foot
    names_all = [n for pl in plates for n in pl]
    prefix = os.path.commonprefix(names_all) if len(names_all) > 1 else ""
    prefix = prefix[:prefix.rfind("-") + 1] if "-" in prefix else ""

    def short(n): return n[len(prefix):] or n

    def wrap(text, width):
        lines, cur = [], ""
        for w in text.split(", "):
            if cur and len(cur) + len(w) + 2 > width:
                lines.append(cur + ",")
                cur = w
            else:
                cur = f"{cur}, {w}" if cur else w
        return lines + [cur]

    def X(x): return pad + (x - x0) * s
    def Y(y): return pad + head + (y1 - y) * s

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}" '
           'font-family="Segoe UI, Arial, sans-serif">\n<rect width="100%" height="100%" fill="#ffffff"/>\n',
           f'<text x="{pad}" y="{pad + 4}" font-size="20" font-weight="600">{escape(title)}: '
           f'{len(plates)} plates, {bed[0]:g} x {bed[1]:g} mm bed, top view</text>\n']
    if note:
        cut = note.rfind(" | ") if len(note) * 6.8 > W - 2 * pad else -1
        for k, line in enumerate([note] if cut < 0 else [note[:cut + 2], "    " + note[cut + 3:]]):
            out.append(f'<text x="{pad}" y="{pad + 26 + 15 * k}" font-size="12.5" fill="#555">{escape(line)}</text>\n')
    by_name = {p[0]: p for p in placed}
    for i, names in enumerate(plates):
        ox, oy = origins[i]
        out.append(f'<rect x="{X(ox):.1f}" y="{Y(oy + bed[1]):.1f}" width="{bed[0] * s:.1f}" height="{bed[1] * s:.1f}" '
                   'rx="6" fill="#eceff1" stroke="#90a4ae" stroke-width="1.5"/>\n')
        grid = [f'M{X(ox + g):.1f},{Y(oy):.1f} V{Y(oy + bed[1]):.1f}' for g in np.arange(10, bed[0], 10)]
        grid += [f'M{X(ox):.1f},{Y(oy + g):.1f} H{X(ox + bed[0]):.1f}' for g in np.arange(10, bed[1], 10)]
        out.append(f'<path d="{" ".join(grid)}" stroke="#d5dde1" stroke-width="0.6" fill="none"/>\n')
        out.append(f'<text x="{X(ox):.1f}" y="{Y(oy + bed[1]) - 8:.1f}" font-size="16" font-weight="600" '
                   f'fill="#37474f">Plate {i + 1}</text>\n')
        for n in names:
            _, v, f, c = by_name[n]
            col = c if c and HEX.fullmatch(c) else "#B0B0B0"
            out.append(f'<path d="{_svg_path(footprint(v, f), X, Y)}" fill="{col}" fill-rule="evenodd" '
                       'stroke="#263238" stroke-width="0.8"><title>' + escape(n) + '</title></path>\n')
        for k, line in enumerate(wrap(", ".join(short(n) for n in names), int(bed[0] * s / 6.6))):
            out.append(f'<text x="{X(ox):.1f}" y="{Y(oy) + 17 + 15 * k:.1f}" font-size="12" fill="#37474f">'
                       f'{escape(line)}</text>\n')
    out.append("</svg>\n")
    return "".join(out)


def _write_plates(path: Path, parts, summary, title: str, bed, plates, presets: dict) -> dict:
    """One Bambu/Orca plate per entry of `plates` (lists of STL stems), each centred on its bed."""
    if not bed:
        raise ValueError("--plate needs --bed")
    by_name = {p[0]: p for p in parts}
    unknown = [n for pl in plates for n in pl if n not in by_name]
    if unknown:
        raise ValueError(f"--plate names not among the STLs: {', '.join(unknown)}")
    placed, plate_ids = [], []
    for i, names in enumerate(plates):
        ox, oy = plate_origin(i, len(plates), bed)
        allv = np.vstack([by_name[n][1] for n in names])
        lo, hi = allv.min(0), allv.max(0)
        shift = np.array([ox + bed[0] / 2 - (lo[0] + hi[0]) / 2, oy + bed[1] / 2 - (lo[1] + hi[1]) / 2, 0.0])
        ids = []
        for n in names:
            _, v, f, c = by_name[n]
            ids.append(len(placed) + 2)                 # model_xml numbers objects from 2
            placed.append((n, v + shift, f, c))
        plate_ids.append((", ".join(names), ids))
    application, config, presets_used = BBL_APPLICATION, None, None
    if len(bed) >= 3:
        try:
            config, application, presets_used = bambu.project_config(
                bed, float(presets.get("nozzle") or 0.4), float(presets.get("layer") or 0.2),
                str(presets.get("material") or "PLA"), presets.get("printer"))
        except LookupError as exc:
            print(f"3mf: WARNING no Bambu project config ({exc}); Bambu Studio will load all parts onto one plate",
                  file=sys.stderr)
    else:
        print("3mf: WARNING --bed has no height, so no Bambu project config; Bambu Studio will load all parts "
              "onto one plate (use --bed XxYxZ)", file=sys.stderr)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.tmp")
    with zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("3D/3dmodel.model", model_xml(placed, title, application=application))
        z.writestr("Metadata/model_settings.config", model_settings_xml(plate_ids))
        if config is not None:
            z.writestr("Metadata/project_settings.config", json.dumps(config, indent=4, ensure_ascii=False) + "\n")
    tmp.replace(path)
    svg = path.with_name(path.stem + "-plates.svg")
    note = (f"Bambu Studio presets: {presets_used.split(' (profiles')[0]}" if presets_used
            else "no Bambu project config: Bambu Studio will show one plate")
    svg.write_text(plates_svg(placed, plates, bed, title, note), encoding="utf-8")
    keep = {n for pl in plates for n in pl}
    return {"file": path.name, "plates": [list(pl) for pl in plates], "plates_svg": svg.name,
            "bambu_presets": presets_used, "objects": [s for s in summary if s["name"] in keep]}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pack STL parts into a 3MF file.")
    ap.add_argument("out", help="output .3mf path")
    ap.add_argument("stl", nargs="+", help="input .stl files (one object each)")
    ap.add_argument("--title", default="", help="title stored in the 3MF metadata")
    ap.add_argument("--bed", default=None, metavar="XxY[xZ]",
                    help="centre the parts on a bed of this size, e.g. 220x220 (plates: with the height, 180x180x180)")
    ap.add_argument("--copies", type=int, default=1, help="copies of the part set on the plate (spec print.quantity)")
    ap.add_argument("--plate", action="append", default=[], metavar="STEM[,STEM...]",
                    help="one Bambu Studio / OrcaSlicer plate with these STL stems (repeatable); needs --bed")
    ap.add_argument("--nozzle", type=float, default=0.4, help="plates: nozzle for the Bambu printer preset")
    ap.add_argument("--layer", type=float, default=0.2, help="plates: layer height for the Bambu process preset")
    ap.add_argument("--material", default="PLA", help="plates: filament type for the Bambu filament preset")
    ap.add_argument("--printer", default=None,
                    help='plates: Bambu printer model when several share the bed size, e.g. "Bambu Lab A1"')
    args = ap.parse_args(argv)
    if not 1 <= args.copies <= 50:
        print("--copies must be 1 to 50", file=sys.stderr)
        return 2
    out = Path(args.out)
    if out.suffix.lower() != ".3mf":
        print("output must end in .3mf", file=sys.stderr)
        return 2
    bed = None
    if args.bed:
        try:
            bed = [float(x) for x in args.bed.lower().split("x")[:3]]
        except ValueError:
            print("--bed must look like 220x220", file=sys.stderr)
            return 2
    plates = [[n.strip() for n in p.split(",") if n.strip()] for p in args.plate]
    if plates and args.copies > 1:
        print("--plate and --copies cannot be combined", file=sys.stderr)
        return 2
    try:
        info = write_3mf(out, args.stl, args.title or out.stem, bed=bed, copies=args.copies, plates=plates or None,
                         presets={"nozzle": args.nozzle, "layer": args.layer, "material": args.material,
                                  "printer": args.printer})
    except (ValueError, OSError) as exc:
        print(f"3mf: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
