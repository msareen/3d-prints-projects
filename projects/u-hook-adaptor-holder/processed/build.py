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
NAME = "u-hook-adaptor-holder"   # output file stem: a-z, 0-9 and dashes only
MATERIAL = "PLA"                 # user's choice (round 2); sets density for the mass estimate
COLOR = {"": "#4f8cff", "pin-test": "#ff9f40"}  # preview colours per part, viewer only

PRINTER_BED = (180, 180, 180)    # same printer as the earlier projects (180 mm cube)
NOZZLE = 0.4                     # nozzle diameter; minimum wall = 2 x NOZZLE
LAYER = 0.2                      # layer height; flat feature heights are multiples of it
OVERHANG_LIMIT = 45              # degrees from vertical this printer manages without support
SUPPORTS_ALLOWED = False         # no supports: pins are point-down teardrops, mesh openings are 45 deg diamonds
EXPECTED_BODIES = 1              # one solid per part; a second body means a loose piece

# Model frame = real frame (printed upright, bottom frame on the bed):
# X = left -> right seen from the front, 0 at the left outer face;
# Y = towards the rack, 0 = back face that rests on the upright, cup at -Y, pins at +Y;
# Z = up, 0 = underside of the bottom frame.

# --- the brick (caliper values from the user), standing on its end ---
BRICK_L = 90.4                   # D1 brick length, vertical (Z): AC input on top, DC + USB-A at the bottom
BRICK_D = 25.6                   # D2 brick thickness, front-to-back (Y)
BRICK_W = 50.6                   # D3 brick width, left-right along the rack (X)
CRADLE_SLACK = 0.5               # D4 extra per-side room on top of the free fit: drop-in, no rubbing
CLEAR = FITS["free"]             # per-side free fit from the material profile (0.30 for PLA)

# --- the cup (J seen from the side) ---
BACK_T = 4.0                     # D5 back wall thickness: carries the pins
WALL_T = 3.0                     # D6 front and side wall thickness
FLOOR_T = 3.0                    # D7 bottom frame thickness (15 layers)
BACK_H = 70.0                    # D8 back wall height above the frame top: brick top 20 mm proud, AC plug free
LIP_H = 30.0                     # D9 front and side wall height above the frame top
LEDGE_W = 5.0                    # D33 bottom ledge under the brick's front and back edges (Y)

# --- keyhole pins ---
PIN_COL_W = 20.0                 # D12 solid column round the pins (X), at the left end as in Frontview.png
PIN_X = 10.0                     # D13 pin centre from the left end = PIN_COL_W / 2
LOWER_PIN_Z = 27.0               # D14 lower pin centre height above the frame underside
PIN_PITCH = 38.0                 # D15 keyhole pitch, centre to centre (scaled from the ruler photo)
STRIP_TOP_MARGIN = 8.0           # D16 back wall top above the upper pin centre
NECK_D = 5.6                     # D17 groove width across (X): rev 1 sample fitted the slot well (user), kept
NECK_L = 1.7                     # D18 groove width (Y): 1.6 mm steel (user caliper) + 0.1 (user)
HEAD_D = 9.6                     # D19 pin head width (X): rev 1 7.6 + 2 (user, rev 2); 1.7 grip each side of the slot
HEAD_T = 3.0                     # D20 pin head thickness (Y)

# --- pin test sample (second part: the pin column alone, to test the fit in the rack first) ---
SAMPLE_GAP = 10.0                # D35 gap between holder and sample on the plate (X)
SAMPLE_PIN_Z = 8.0               # D36 sample lower pin centre above the bed (head clears the bed by 4.2)
FOOT_D = 14.0                    # D37 sample foot depth in front of its plate (-Y): keeps it standing
FOOT_T = 2.0                     # D38 sample foot thickness

# --- ventilation mesh (diamonds: 45 deg roofs print without support) ---
DIAMOND_D = 10.0                 # D21 diamond opening, corner to corner (both directions)
DIAMOND_PITCH = 14.0             # D22 diamond lattice pitch: 2.8 mm webs
MESH_BORDER = 4.0                # D23 solid border round every mesh field

# derived (not spec inputs)
SIDE = CLEAR + CRADLE_SLACK
INNER_W = BRICK_W + 2 * SIDE
INNER_D = BRICK_D + 2 * SIDE
OUTER_X = INNER_W + 2 * WALL_T
Y_FRONT = -(BACK_T + INNER_D + WALL_T)
Z_BACK_TOP = FLOOR_T + BACK_H
PIN_ZS = (LOWER_PIN_Z, LOWER_PIN_Z + PIN_PITCH)
Y_MID = -(BACK_T + INNER_D / 2)

_HOLDER_PROBES_IN = [
    (PIN_X, -BACK_T / 2, Z_BACK_TOP - 2),                    # pin column is solid
    (PIN_X, NECK_L / 2, LOWER_PIN_Z),                        # lower pin neck
    (PIN_X, NECK_L + HEAD_T / 2, LOWER_PIN_Z + PIN_PITCH),   # upper pin head
    (OUTER_X / 2, -BACK_T - LEDGE_W / 2, FLOOR_T / 2),       # back ledge
    (OUTER_X / 2, Y_FRONT + WALL_T + LEDGE_W / 2, FLOOR_T / 2),  # front ledge
]
_HOLDER_PROBES_OUT = [
    (OUTER_X / 2, Y_MID, FLOOR_T + 40),                      # brick space is empty
    (OUTER_X / 2, Y_MID, FLOOR_T / 2),                       # bottom opening (DC cable + USB-A)
    (WALL_T + 2, Y_MID, FLOOR_T / 2),                        # bottom opening reaches the side walls
]
SAMPLE_X0 = OUTER_X + SAMPLE_GAP
SAMPLE_H = SAMPLE_PIN_Z + PIN_PITCH + STRIP_TOP_MARGIN
PROBES_INSIDE = {
    "": _HOLDER_PROBES_IN,
    "pin-test": [
        (SAMPLE_X0 + PIN_X, NECK_L / 2, SAMPLE_PIN_Z),                   # lower groove core
        (SAMPLE_X0 + PIN_X, NECK_L + HEAD_T / 2, SAMPLE_PIN_Z + PIN_PITCH),  # upper head
        (SAMPLE_X0 + PIN_X, -BACK_T / 2, SAMPLE_H - 2),                  # plate
    ],
}
PROBES_OUTSIDE = {
    "": _HOLDER_PROBES_OUT,
    "pin-test": [(SAMPLE_X0 + PIN_X + (NECK_D + HEAD_D) / 4, NECK_L / 2, SAMPLE_PIN_Z)],  # groove is cut
}
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
from shapely.geometry import Polygon  # noqa: E402  (shapely is part of the skill stack)


def _diamond(cx, cy):
    """2D diamond (square rotated 45 deg) centred on (cx, cy), DIAMOND_D corner to corner."""
    h = DIAMOND_D / 2
    return Polygon([(cx + h, cy), (cx, cy + h), (cx - h, cy), (cx, cy - h)])


def _diamond_field(u0, v0, u1, v1):
    """Diamonds of a staggered lattice that lie fully inside the rectangle u0..u1 x v0..v1.

    The lattice is centred on the rectangle; rows are DIAMOND_PITCH / 2 apart and
    every other row is shifted by DIAMOND_PITCH / 2.
    """
    h = DIAMOND_D / 2
    half = DIAMOND_PITCH / 2
    cu, cv = (u0 + u1) / 2, (v0 + v1) / 2
    out = []
    nv = int((v1 - v0) / half) + 2
    nu = int((u1 - u0) / DIAMOND_PITCH) + 2
    for j in range(-nv, nv + 1):
        v = cv + j * half
        shift = half if j % 2 else 0.0
        for i in range(-nu, nu + 1):
            u = cu + shift + i * DIAMOND_PITCH
            if u - h >= u0 - 1e-6 and u + h <= u1 + 1e-6 and v - h >= v0 - 1e-6 and v + h <= v1 + 1e-6:
                out.append(_diamond(u, v))
    return out


def _xz_cutters(fields, y0, y1):
    """Prisms through a wall in the XZ plane between y0 and y1; shapes drawn as (X, Z)."""
    cut = []
    for poly in fields:
        s = cad.extrude(poly, (y1 - y0) + 2)          # profile in XY, length along +Z
        s = cad.rotate(s, x=90)                        # (x, y, z) -> (x, -z, y): v -> Z, length -> -Y
        cut.append(cad.translate(s, y=y1 + 1))
    return cut


def _yz_cutters(fields, x0, x1):
    """Prisms through a wall in the YZ plane between x0 and x1; shapes drawn as (Y, Z)."""
    cut = []
    for poly in fields:
        s = cad.extrude(poly, (x1 - x0) + 2)          # profile (Y, Z) in XY, length along +Z
        s = cad.rotate(s, x=90)                        # u stays X, v -> Z, length -> -Y
        s = cad.rotate(s, z=90)                        # (x, y, z) -> (-y, x, z): u -> Y, length -> +X
        cut.append(cad.translate(s, x=x0 - 1))
    return cut


def _pin(z):
    """Keyhole pin along +Y: groove (neck) against the back face, then the head.

    Both are point-down teardrops (user, rev 2): 45 deg undersides print without
    support, and the groove's point seats in the round bottom of the keyhole slot.
    """
    neck = cad.rotate(cad.teardrop_hole(NECK_D, NECK_L + 1, axis="y", flat_top=False), y=180)
    head = cad.rotate(cad.teardrop_hole(HEAD_D, HEAD_T, axis="y", flat_top=False), y=180)
    neck = cad.translate(neck, y=(NECK_L + 1) / 2)                 # teardrop_hole is centred: y 0..NECK_L+1
    head = cad.translate(head, y=HEAD_T / 2)                       # y 0..HEAD_T
    neck = cad.translate(neck, x=PIN_X, y=-1, z=z)                 # 1 mm buried in the back wall
    head = cad.translate(head, x=PIN_X, y=NECK_L, z=z)
    return cad.union(neck, head)


def build_part():
    """Upright cup for the brick: back wall with pins, low front and side walls, open-centre bottom."""
    depth = -Y_FRONT
    floor = cad.translate(cad.box(OUTER_X, depth, FLOOR_T, center_xy=False), y=Y_FRONT)
    back = cad.translate(cad.box(OUTER_X, BACK_T, Z_BACK_TOP, center_xy=False), y=-BACK_T)
    front = cad.translate(cad.box(OUTER_X, WALL_T, FLOOR_T + LIP_H, center_xy=False), y=Y_FRONT)
    sides = [cad.translate(cad.box(WALL_T, depth, FLOOR_T + LIP_H, center_xy=False), x=x, y=Y_FRONT)
             for x in (0.0, OUTER_X - WALL_T)]
    body = cad.union(floor, back, front, *sides, *[_pin(z) for z in PIN_ZS])

    # bottom opening: full inner width, between the front and back ledges (DC cable + USB-A plug)
    y_hi = -BACK_T - LEDGE_W
    y_lo = Y_FRONT + WALL_T + LEDGE_W
    opening = cad.translate(cad.box(INNER_W, y_hi - y_lo, FLOOR_T + 2, center_xy=False),
                            x=WALL_T, y=y_lo, z=-1)
    cutters = [opening]

    # back wall mesh, right of the solid pin column
    cutters += _xz_cutters(
        _diamond_field(PIN_COL_W + MESH_BORDER, FLOOR_T + MESH_BORDER, OUTER_X - MESH_BORDER, Z_BACK_TOP - MESH_BORDER),
        -BACK_T, 0.0)
    # front wall mesh
    cutters += _xz_cutters(
        _diamond_field(MESH_BORDER, FLOOR_T + MESH_BORDER, OUTER_X - MESH_BORDER, FLOOR_T + LIP_H - MESH_BORDER),
        Y_FRONT, Y_FRONT + WALL_T)
    # side wall mesh (both sides)
    side_field = _diamond_field(Y_FRONT + WALL_T + MESH_BORDER, FLOOR_T + MESH_BORDER,
                                -BACK_T - MESH_BORDER, FLOOR_T + LIP_H - MESH_BORDER)
    for x0 in (0.0, OUTER_X - WALL_T):
        cutters += _yz_cutters(side_field, x0, x0 + WALL_T)
    holder = cad.difference(body, *cutters)
    return {"": holder, "pin-test": _pin_test()}


def _pin_test():
    """Pin test sample: the holder's pin column (same plate, same pins, same pitch) on a small foot."""
    plate = cad.translate(cad.box(PIN_COL_W, BACK_T, SAMPLE_H, center_xy=False), y=-BACK_T)
    foot = cad.translate(cad.box(PIN_COL_W, FOOT_D, FOOT_T, center_xy=False), y=-BACK_T - FOOT_D)
    pins = [_pin(z) for z in (SAMPLE_PIN_Z, SAMPLE_PIN_Z + PIN_PITCH)]
    return cad.translate(cad.union(plate, foot, *pins), x=SAMPLE_X0)
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
