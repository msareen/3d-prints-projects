#!/usr/bin/env python3
"""Parametric build script for one FDM part (3d-print-design skill template).

Copy this file into a fresh, empty project folder (never inside a cloned
repository or a folder of downloaded files), then:
    python -P build.py            -> runs printcheck, writes out/<NAME>.stl + out/<NAME>.json
    python -P build.py --check    -> runs printcheck only, writes nothing
Set PRINT3D_SKILL_DIR to the skill folder unless it is installed in
~/.claude/skills/3d-print-design.

Three zones:
  PARAMETERS  every number lives here, in millimetres, each with a comment
              saying why it has that value. Iterate by editing only this block.
  GEOMETRY    build_part() turns the parameters into a solid. It uses
              parameter names, never bare numbers (0, 1, 2 and halves are fine).
  HARNESS     below the DO NOT EDIT line: name check, printcheck, export.

Units: mm. Z is up. The part must sit on z = 0 in its print orientation.
This script never contacts a printer; slicing and printing are your steps.
"""
import os
import sys

# Never import code from the project folder. Python puts this script's folder
# first on sys.path, so a planted argparse.py, pathlib.py or cad.py next to
# build.py would run. os and sys are already loaded by the interpreter, so this
# runs before anything that could be shadowed. (`python -P build.py` does the
# same; this keeps plain `python build.py` safe too.)
if not getattr(sys.flags, "safe_path", False):
    _HERE = os.path.realpath(os.path.dirname(os.path.abspath(__file__)))
    sys.path[:] = [p for p in sys.path if os.path.realpath(p or os.getcwd()) != _HERE]

import argparse  # noqa: E402
from pathlib import Path  # noqa: E402


def _skill_scripts() -> Path:
    """Find the skill's scripts/ folder (cad.py + printcheck.py).

    Only two places are trusted: $PRINT3D_SKILL_DIR/scripts and the installed
    skill in ~/.claude/skills/3d-print-design/scripts. Folders around the
    project are never searched, so a repository or download folder that
    happens to contain a scripts/cad.py cannot inject code.
    """
    candidates = []
    env = os.environ.get("PRINT3D_SKILL_DIR")
    if env:
        candidates.append(Path(env).expanduser().resolve() / "scripts")
    candidates.append(Path.home() / ".claude" / "skills" / "3d-print-design" / "scripts")
    for c in candidates:
        if (c / "cad.py").is_file() and (c / "printcheck.py").is_file():
            return c.resolve()
    sys.exit("cannot find the 3d-print-design scripts: set PRINT3D_SKILL_DIR to the skill folder")


sys.path.insert(0, str(_skill_scripts()))
import cad  # noqa: E402
import printcheck  # noqa: E402
from safeio import safe_text  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent
FITS = cad.load_fits(PROJECT_DIR)  # per-side clearances: fits.json if present, else defaults

# ===================== PARAMETERS START (edit only this block) =====================
NAME = "bathroom-plate"          # output file stem: a-z, 0-9 and dashes only
MATERIAL = "PETG"                # spec print.material: wet shower area
COLOR = "#7fc8c0"                # preview colour in the viewer only, not sent anywhere

PRINTER_BED = (180, 180, 180)    # spec print.printer_bed: Bambu Lab A1 mini
NOZZLE = 0.4                     # spec print.nozzle
LAYER = 0.2                      # spec print.layer
OVERHANG_LIMIT = 45              # degrees from vertical this printer manages without support
SUPPORTS_ALLOWED = False         # spec print.supports
EXPECTED_BODIES = 1              # one solid plate

LEG_L = 170.0                    # D6 wall-edge length = square side (bed 180 - 2 x 5 margin)
BRACKET_FAR = 152.4              # D7 corner to the far edge of each bracket (given: 6 in); only checked, not modelled
FRONT_R = 40.0                   # D17 radius of the front corner (opposite the wall corner): the subtle curve
PLATE_T = 7.8                    # D3 plate thickness: glass 7.9 rounded down to 39 layers, fits the clamp slot
CORNER_R = 4.0                   # D12 radius of the other three corners (wall corner and both wall-edge tips)
TOP_R = 1.2                      # D13 top edge roundover radius (6 layers)
FOOT_CHAMFER = 0.4               # D14 bottom elephant-foot chamfer (design rules)

_MID_Z = PLATE_T / 2
PROBES_INSIDE = [
    (LEG_L / 2, LEG_L / 2, _MID_Z),                    # plate body is solid
    (LEG_L - 15.0, LEG_L - 15.0, _MID_Z),              # inside the front-corner arc
    (BRACKET_FAR - 2.0, 30.0, _MID_Z),                 # plate is there inside bracket A at its far edge
    (30.0, BRACKET_FAR - 2.0, _MID_Z),                 # same at bracket B
]
PROBES_OUTSIDE = [
    (LEG_L - 2.0, LEG_L - 2.0, _MID_Z),                # front corner is cut by the R40 arc
    (0.5, 0.5, _MID_Z),                                # wall corner is rounded
    (LEG_L - 0.5, 0.5, _MID_Z),                        # tip on wall A is rounded
]
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
import math  # noqa: E402
import shapely  # noqa: E402


def outline2d():
    """Square on the two wall edges; small radius on three corners, FRONT_R on the corner opposite the walls."""
    square = cad.box2d(0.0, 0.0, LEG_L, LEG_L)
    rounded = square.buffer(-CORNER_R, join_style="mitre").buffer(CORNER_R, join_style="round", quad_segs=16)
    c = LEG_L - FRONT_R
    corner_cut = cad.box2d(c, c, LEG_L, LEG_L).difference(
        shapely.Point(c, c).buffer(FRONT_R, quad_segs=64))
    return rounded.difference(corner_cut)


def build_part():
    """Solid plate: chamfered body up to the roundover, then layer-stepped quarter-round top edge."""
    shape = outline2d()
    body_h = PLATE_T - TOP_R
    parts = [cad.chamfered_extrude(shape, body_h, bottom=FOOT_CHAMFER)]
    steps = round(TOP_R / LAYER)
    for k in range(steps):
        dz = (k + 0.5) * LAYER                         # height of this slice's middle above the roundover start
        inset = TOP_R - math.sqrt(TOP_R ** 2 - dz ** 2)
        layer = shape.buffer(-inset, join_style="round", quad_segs=16)
        parts.append(cad.extrude(layer, LAYER + (0.01 if k < steps - 1 else 0.0), z0=body_h + k * LAYER))
    return cad.union(*parts)
# ====================== GEOMETRY END ======================


# ============ HARNESS: DO NOT EDIT BELOW THIS LINE ============
def _per_part(value, suffix):
    return value.get(suffix, value.get("", None)) if isinstance(value, dict) else value


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=f"Build {NAME} and check it before export.")
    ap.add_argument("--out", default="out", help="output folder inside the project folder (default out)")
    ap.add_argument("--check", action="store_true", help="run printcheck only, write nothing")
    ap.add_argument("--thin-walls", type=int, default=400, metavar="N",
                    help="surface samples for the thin wall check (0 to skip)")
    args = ap.parse_args(argv)
    g = globals()
    try:
        name = cad.validate_name(g["NAME"])
        out_dir = cad.safe_out_dir(PROJECT_DIR, args.out)
    except ValueError as exc:
        print(f"refusing: {safe_text(exc)}", file=sys.stderr)
        return 2

    parts = build_part()
    if not isinstance(parts, dict):
        parts = {"": parts}
    results = []
    for suffix, solid in parts.items():
        try:
            part_name = name if not suffix else cad.validate_name(f"{name}-{suffix}")
        except ValueError as exc:
            print(f"refusing: {safe_text(exc)}", file=sys.stderr)
            return 2
        mesh = cad.to_trimesh(solid)
        res = printcheck.check_printable(
            mesh, bed=g["PRINTER_BED"], layer=g["LAYER"], nozzle=g["NOZZLE"],
            overhang_deg=g["OVERHANG_LIMIT"], supports=g["SUPPORTS_ALLOWED"],
            expected_bodies=_per_part(g["EXPECTED_BODIES"], suffix),
            thin_wall_samples=args.thin_walls,
            probes_inside=_per_part(g.get("PROBES_INSIDE", ()), suffix) or (),
            probes_outside=_per_part(g.get("PROBES_OUTSIDE", ()), suffix) or (),
        )
        print(res.summary(part_name))
        results.append((part_name, suffix, mesh, res))

    failed = [r for r in results if not r[3].ok]
    if failed:
        print(f"\nprintcheck failed for {', '.join(r[0] for r in failed)}: nothing written. "
              "Fix the parameters or the geometry and run again.", file=sys.stderr)
        return 1
    if args.check:
        print("\ncheck only: nothing written")
        return 0
    params = cad.param_snapshot(g)
    params["FITS"] = FITS
    for part_name, suffix, mesh, res in results:
        try:
            stl, meta = cad.write_part(out_dir, part_name, mesh, res, material=g["MATERIAL"], params=params,
                                       color=_per_part(g.get("COLOR"), suffix), bed=g["PRINTER_BED"])
        except (ValueError, OSError) as exc:
            print(f"refusing: {safe_text(exc)}", file=sys.stderr)
            return 2
        print(f"wrote {stl.relative_to(PROJECT_DIR)} and {meta.relative_to(PROJECT_DIR)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
