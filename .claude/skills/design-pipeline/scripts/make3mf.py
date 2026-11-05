#!/usr/bin/env python3
"""make3mf.py: pack checked STL parts into one 3MF file (3MF Core spec, millimetres).

Each STL becomes one named object with its own display colour (from the part's
JSON metadata `preview_color`, if any), placed exactly where the build put it.
Slicers (PrusaSlicer, Bambu Studio, OrcaSlicer, Cura) open it as one project
with separate objects, which keeps multi-part and multi-colour designs together.

    python -P make3mf.py out.3mf part-a.stl part-b.stl --title "wall hook"

Run with the 3d-print-design venv interpreter (needs trimesh to read STL).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

import numpy as np
import trimesh

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


def model_xml(parts, title: str) -> str:
    """parts: list of (name, vertices (n,3), faces (m,3), colour '#rrggbb' or None)."""
    out = ['<?xml version="1.0" encoding="UTF-8"?>\n'
           '<model unit="millimeter" xml:lang="en-US" '
           'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n',
           f' <metadata name="Title">{escape(title)}</metadata>\n',
           ' <metadata name="Application">design-pipeline (Claude Code skill)</metadata>\n',
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


def write_3mf(path: Path, stl_paths, title: str, bed=None) -> dict:
    """bed = (x, y): move all parts together so their footprint is centred on the bed.

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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Pack STL parts into a 3MF file.")
    ap.add_argument("out", help="output .3mf path")
    ap.add_argument("stl", nargs="+", help="input .stl files (one object each)")
    ap.add_argument("--title", default="", help="title stored in the 3MF metadata")
    ap.add_argument("--bed", default=None, metavar="XxY", help="centre the parts on a bed of this size, e.g. 220x220")
    args = ap.parse_args(argv)
    out = Path(args.out)
    if out.suffix.lower() != ".3mf":
        print("output must end in .3mf", file=sys.stderr)
        return 2
    bed = None
    if args.bed:
        try:
            bed = [float(x) for x in args.bed.lower().split("x")[:2]]
        except ValueError:
            print("--bed must look like 220x220", file=sys.stderr)
            return 2
    try:
        info = write_3mf(out, args.stl, args.title or out.stem, bed=bed)
    except (ValueError, OSError) as exc:
        print(f"3mf: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(info))
    return 0


if __name__ == "__main__":
    sys.exit(main())
