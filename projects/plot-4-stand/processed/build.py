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
import numpy as np  # noqa: E402
import shapely  # noqa: E402
import printcheck  # noqa: E402
from safeio import safe_text  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent
FITS = cad.load_fits(PROJECT_DIR)  # per-side clearances: fits.json if present, else defaults

# ===================== PARAMETERS START (edit only this block) =====================
NAME = "plot-4-stand"          # output file stem: a-z, 0-9 and dashes only
MATERIAL = "PLA"                 # spec print.material
COLOR = "#2f6fe0"                # preview colour in the viewer only, not sent anywhere

PRINTER_BED = (250, 210, 220)    # spec print.printer_bed (Prusa MK4 class; Bambu beds are larger)
NOZZLE = 0.4                     # spec print.nozzle
LAYER = 0.2                      # spec print.layer
OVERHANG_LIMIT = 45              # degrees from vertical this printer manages without support
SUPPORTS_ALLOWED = False         # spec print.supports
EXPECTED_BODIES = 1              # one solid

# --- half ring (footprint) ---
OUTER_W = 95.4                   # D1 outer width across the U (estimated, mat photo 213638)
BAND_W = 20.4                    # D2 ring band width at the arm ends (measured, 213829)
RIM_H = 10.0                     # D5 ring wall height overall (estimated, Q3)
FLOOR_T = 1.6                    # D6 floor thickness (estimated, Q4)
WALL_OUT = 1.8                   # D7 outer curved wall thickness (estimated, Q4)
WALL_IN = 1.5                    # D8 inner curved wall thickness (estimated, Q4)
END_WALL = 1.5                   # D9 arm end wall thickness (estimated, Q4)
FOOT_CHAMFER = 0.4               # D19 bottom elephant-foot chamfer (design rules)

# --- handle: U-channel that takes the board's side rail ---
HANDLE_W = 20.6                  # D10 handle outer width (measured, 213755)
HANDLE_H = 9.6                   # D15 handle height (measured, 213910)
HANDLE_FLOOR = 2.0               # D16 handle floor thickness (estimated, Q4)
OVERALL_L = 69.5                 # D17 arm-end faces to handle end (estimated, mat photo 213638)
RAIL_EDGE_T = 12.8               # D20 board rail end (narrow section), held by the lips (measured, 215353)
RAIL_IN_T = 15.0                 # D21 board rail body (measured, 215421): sets the wide part below the lips
EDGE_H = 3.0                     # D25 lip depth: vertical catch face from the handle top down (estimated, Q6)
LEAD_IN = 0.5                    # D26 45 deg lead-in on the lips so the rail pushes in
CH_CLEAR = FITS["snug"]          # per-side clearance in the wide part, PLA snug 0.10 (spec A6)
LIP_CLEAR = FITS["press"]        # per-side clearance at the lips, PLA press 0.05: prints about 12.7 like the original catch

R_OUT = OUTER_W / 2              # D3 outer arc radius
R_IN = R_OUT - BAND_W            # D4 inner arc radius
CH_BOT = RAIL_EDGE_T + 2 * LIP_CLEAR  # D22 printed opening between the lips
CH_TOP = RAIL_IN_T + 2 * CH_CLEAR     # D23 printed width of the channel below the lips
EPS = 0.01                       # overlap so booleans never leave zero-thickness skins

_MID_R = (R_IN + R_OUT) / 2
_WALL_X = (CH_TOP + HANDLE_W) / 4               # inside a handle side wall
_EDGE_X = (CH_BOT + CH_TOP) / 4                  # across the lip width
_LIP_Z = HANDLE_H - EDGE_H / 2                   # half way down a lip
PROBES_INSIDE = [
    (0.0, _MID_R, FLOOR_T / 2),                  # ring floor is solid
    (R_OUT - WALL_OUT / 2, 0.5, RIM_H / 2),      # outer wall at the arm end (x = +R_OUT side)
    (_WALL_X, R_OUT + 10.0, HANDLE_H / 2),       # handle side wall is solid
    (0.0, R_OUT + 10.0, HANDLE_FLOOR / 2),       # handle floor is solid
    (_EDGE_X, R_OUT + 10.0, _LIP_Z),             # lip is solid
]
PROBES_OUTSIDE = [
    (0.0, _MID_R, RIM_H / 2),                    # ring pocket is empty
    (0.0, R_OUT + 10.0, _LIP_Z),                 # opening is empty
    (_EDGE_X, R_OUT + 10.0, HANDLE_FLOOR + 1.0),  # wide part under the lip is empty
    (0.0, R_IN / 2, RIM_H / 2),                  # inside the U is empty
]
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
def _half_ring(r_in, r_out, n=180):
    """Half annulus on the +Y side, ends on the X axis; r_in = 0 gives a half disc."""
    a = np.linspace(0.0, np.pi, n)
    outer = [(r_out * np.cos(t), r_out * np.sin(t)) for t in a]
    inner = [(r_in * np.cos(t), r_in * np.sin(t)) for t in a[::-1]] if r_in > 0 else [(0.0, 0.0)]
    return shapely.Polygon(outer + inner)


def build_part():
    """Half-ring tray (floor down, open up) plus a U-channel handle on +Y."""
    ring = cad.chamfered_extrude(_half_ring(R_IN, R_OUT), RIM_H, bottom=FOOT_CHAMFER)
    # handle overlaps into the outer wall; the pocket cut below clears any overlap inside the tray
    handle2d = cad.box2d(-HANDLE_W / 2, R_OUT - WALL_OUT, HANDLE_W / 2, OVERALL_L)
    handle = cad.chamfered_extrude(handle2d, HANDLE_H, bottom=FOOT_CHAMFER)
    body = cad.union(ring, handle)

    # ring pocket: open top, leaves floor, inner/outer walls and the two arm end walls
    pocket2d = _half_ring(R_IN + WALL_IN, R_OUT - WALL_OUT)
    pocket2d = pocket2d.intersection(cad.box2d(-R_OUT, END_WALL, R_OUT, R_OUT))
    pocket = cad.extrude(pocket2d, RIM_H, z0=FLOOR_T)

    # clip channel: lips at the opening narrow it to CH_BOT; below them it widens to CH_TOP.
    # Lip underside is 45 deg so it prints without support; a small lead-in on top guides the rail.
    over = 1.0
    o, v = CH_BOT / 2, CH_TOP / 2
    z_lip = HANDLE_H - EDGE_H                    # bottom of the vertical catch face
    z_wide = z_lip - (v - o)                     # where the 45 deg underside meets the side wall
    right = [(v, HANDLE_FLOOR), (v, z_wide), (o, z_lip), (o, HANDLE_H - LEAD_IN),
             (o + LEAD_IN + over, HANDLE_H + over)]          # 45 deg lead-in, carried past the top
    prof = shapely.Polygon(right + [(-x, z) for x, z in reversed(right)])
    length = OVERALL_L - R_IN + over
    channel = cad.rotate(cad.extrude(prof, length), x=90)      # profile Y -> Z, extrusion -> -Y
    channel = cad.translate(channel, y=OVERALL_L + over)
    channel = cad.difference(channel, cad.extrude(_half_ring(0, R_OUT - EPS), RIM_H + 2 * over, z0=-over))

    return cad.difference(body, pocket, channel)
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
