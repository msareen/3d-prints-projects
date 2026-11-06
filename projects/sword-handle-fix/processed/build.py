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
import manifold3d as m3  # noqa: E402
import numpy as np  # noqa: E402
import shapely  # noqa: E402
import printcheck  # noqa: E402
from safeio import safe_text  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent
FITS = cad.load_fits(PROJECT_DIR)  # per-side clearances: fits.json if present, else defaults

# ===================== PARAMETERS START (edit only this block) =====================
NAME = "sword-handle-fix"        # output file stem: a-z, 0-9 and dashes only
MATERIAL = "PLA"                 # spec print.material
COLOR = "#2b2b2b"                # preview colour in the viewer only (black, like the handle)

PRINTER_BED = (250, 210, 220)    # spec print.printer_bed (Prusa MK4 class; Bambu beds are larger)
NOZZLE = 0.4                     # spec print.nozzle
LAYER = 0.2                      # spec print.layer
OVERHANG_LIMIT = 45              # degrees from vertical this printer manages without support
SUPPORTS_ALLOWED = False         # spec print.supports
EXPECTED_BODIES = 1              # one solid

# --- the handle the cap slides over (straight bore at the largest readings, spec A1) ---
HANDLE_W = 31.6                  # D1 handle width across the chevron face, largest reading (measured, 093337)
HANDLE_T = 28.3                  # D2 handle thickness, largest reading (measured, 093520)
SLEEVE_L = 15.0                  # D4 how far the cap reaches over the handle (given, brief; 093612 '15.1')
BORE_R = 8.0                     # D5 bore corner radius: rounded barrel section (estimated, 093318)
CLEAR = FITS["free"]             # D8 per-side glue gap, PLA free 0.30

# --- the cap ---
WALL = 2.4                       # D6 side wall: 6 perimeters of 0.4
FLOOR_T = 2.4                    # D7 closed end: 12 layers
VENT_D = 3.0                     # D14 vent hole in the closed end: air and extra glue escape
TOP_CHAMFER = 0.6                # D16 outer chamfer at the open rim
LEAD_IN = 0.6                    # D17 45 deg lead-in inside the open rim

# --- design: outward bulge + chevron grooves (user: 'little designer', 'outward bulge') ---
BULGE = 2.0                      # D18 extra outward bulge per side at mid-height (circular arc profile)
SLICES = 59                      # profile slices over the height (0.3 mm apart, one at mid-height)
CHEV_DEPTH = 0.7                 # D19 chevron groove depth at the shelf
CHEV_RAMP_DEG = 15               # D20 groove ramp angle to the surface: keeps the underside under 45 deg
CHEV_PITCH = 3.5                 # D21 vertical spacing of the chevrons
CHEV_Z0 = 6.0                    # D22 height of the lowest chevron apex
CHEV_N = 3                       # chevrons per wide face
CHEV_ANGLE = 25                  # D23 chevron arm angle below horizontal (estimated, handle in 093346)
CHEV_FADE = 4.0                  # arms run this far past the flat face so the groove fades round the corner

BORE_W = HANDLE_W + 2 * CLEAR    # D9 printed bore width 32.2
BORE_T = HANDLE_T + 2 * CLEAR    # D10 printed bore thickness 28.9
OUT_W = BORE_W + 2 * WALL        # D11 outer width at both ends 37.0
OUT_T = BORE_T + 2 * WALL        # D12 outer thickness at both ends 33.7
HEIGHT = FLOOR_T + SLEEVE_L      # D13 overall height 17.4
EPS = 0.01                       # overlap so booleans never leave zero-thickness skins

PROBES_INSIDE = [
    ((BORE_W + OUT_W) / 4, 0.0, HEIGHT / 2),   # side wall (X) is solid
    (0.0, (BORE_T + OUT_T) / 4, HEIGHT / 2),   # side wall (Y) is solid
    (0.0, BORE_T / 4, FLOOR_T / 2),            # closed end is solid beside the vent
    (0.0, OUT_T / 2 + BULGE - 0.3, HEIGHT / 2),  # bulge is solid at mid-height (front face, x = 0)
]
PROBES_OUTSIDE = [
    (0.0, 0.0, HEIGHT / 2),                    # bore is empty
    (0.0, 0.0, FLOOR_T / 2),                   # vent hole is open
    (0.0, OUT_T / 2 + BULGE + 0.3, HEIGHT / 2),  # nothing beyond the bulge
]
_R_ARC = ((HEIGHT / 2) ** 2 + BULGE ** 2) / (2 * BULGE)
for _i in range(CHEV_N):                       # each chevron groove is cut at its apex (x = 0), both faces
    _z = CHEV_Z0 + _i * CHEV_PITCH + 0.4
    _y = BORE_T / 2 + WALL + (_R_ARC ** 2 - (_z - HEIGHT / 2) ** 2) ** 0.5 - (_R_ARC - BULGE) - 0.3
    PROBES_OUTSIDE += [(0.0, _y, _z), (0.0, -_y, _z)]
    PROBES_INSIDE += [(0.0, _y, _z - 0.8)]     # and the wall just below the shelf is solid
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
_ARC_HALF = HEIGHT / 2
_ARC_R = (_ARC_HALF ** 2 + BULGE ** 2) / (2 * BULGE)   # circle through both ends and the bulge peak


def _offset(z):
    """Outer surface distance from the bore at height z: WALL at both ends, WALL + BULGE at mid-height."""
    return WALL + np.sqrt(_ARC_R ** 2 - (z - _ARC_HALF) ** 2) - (_ARC_R - BULGE)


def _slope(z):
    """d(offset)/dz of the bulge profile."""
    return -(z - _ARC_HALF) / np.sqrt(_ARC_R ** 2 - (z - _ARC_HALF) ** 2)


def _outline(off):
    return cad.rounded_rect(BORE_W + 2 * off, BORE_T + 2 * off, BORE_R + off)


def _slice(off, z):
    return cad.extrude(_outline(off), EPS, z0=z)


def _body():
    """Bulged outer body: convex hulls between neighbouring profile slices, top rim chamfered."""
    zs = np.linspace(0.0, HEIGHT - TOP_CHAMFER, SLICES)
    sl = [_slice(_offset(z), z - EPS if z > 0 else 0.0) for z in zs]
    parts = [m3.Manifold.batch_hull([a, b]) for a, b in zip(sl[:-1], sl[1:])]
    top_off = _offset(HEIGHT)
    parts.append(m3.Manifold.batch_hull([sl[-1], _slice(top_off - TOP_CHAMFER, HEIGHT - EPS)]))
    return cad.union(*parts)


def _chevron_arm(z_apex):
    """Sawtooth groove cutter for the right arm of one chevron on the +Y face.

    Profile in the local (n = outward normal, u = up the face) plane: a flat shelf at u = 0 that
    faces up, CHEV_DEPTH deep, and a ramp at CHEV_RAMP_DEG back out to the surface above it.
    """
    ramp = CHEV_DEPTH / np.tan(np.radians(CHEV_RAMP_DEG))
    out = 1.5
    prof = shapely.Polygon([(-CHEV_DEPTH, 0.0), (out, 0.0), (out, ramp * (CHEV_DEPTH + out) / CHEV_DEPTH)])
    a = np.radians(CHEV_ANGLE)
    x0, x1 = -0.3, (BORE_W - 2 * BORE_R) / 2 + CHEV_FADE
    length = (x1 - x0) / np.cos(a)
    xm = (x0 + x1) / 2
    zm = z_apex - xm * np.tan(a)
    k = _slope(zm)
    n = np.array([0.0, 1.0, -k]) / np.hypot(1.0, k)
    t = np.array([0.0, k, 1.0]) / np.hypot(1.0, k)
    w = np.cos(a) * np.array([1.0, 0.0, 0.0]) - np.sin(a) * t
    u = np.cross(n, w)
    if u[2] < 0:
        u = -u
    if np.linalg.det(np.column_stack([n, u, w])) < 0:
        w = -w
    origin = np.array([xm, BORE_T / 2 + _offset(zm), zm])
    m = np.column_stack([n, u, w, origin])
    return cad.extrude(prof, length, z0=-length / 2).transform(m.tolist())


def _chevrons():
    arms = []
    for i in range(CHEV_N):
        right = _chevron_arm(CHEV_Z0 + i * CHEV_PITCH)
        arms += [right, cad.mirror(right, "x")]
    front = cad.union(*arms)
    return cad.union(front, cad.mirror(front, "y"))


def build_part():
    """Closed-end cap: closed end on the bed, open rim up, straight bore, bulged and grooved outside."""
    bore2d = cad.rounded_rect(BORE_W, BORE_T, BORE_R)
    body = _body()
    bore = cad.extrude(bore2d, SLEEVE_L + EPS, z0=FLOOR_T)
    # lead-in: a 45 deg flare from the bore outline at HEIGHT - LEAD_IN out to bore + LEAD_IN at the rim
    # built as a hull from the bore's own outline, so its lower edge shares the bore's vertices exactly
    flare = m3.Manifold.batch_hull([cad.extrude(bore2d, EPS, z0=HEIGHT - LEAD_IN - EPS),
                                    cad.extrude(bore2d.buffer(LEAD_IN + EPS), EPS, z0=HEIGHT)])
    vent = cad.translate(cad.cylinder(VENT_D, FLOOR_T + 2 * EPS), z=-EPS)
    return cad.difference(body, bore, flare, vent, _chevrons())
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
