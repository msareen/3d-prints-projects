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
NAME = "u-hook-cable-manager"    # output file stem: a-z, 0-9 and dashes only
MATERIAL = "PLA"                 # user's choice
COLOR = {"": "#4f8cff"}          # preview colour, viewer only

PRINTER_BED = (180, 180, 180)    # same printer as the earlier projects (180 mm cube)
NOZZLE = 0.4                     # nozzle diameter; minimum wall = 2 x NOZZLE
LAYER = 0.2                      # layer height
OVERHANG_LIMIT = 45              # degrees from vertical this printer manages without support
SUPPORTS_ALLOWED = True          # user: minimal support; "on build plate only": just under the plate's back (4.7 mm)
EXPECTED_BODIES = 3              # print in place: plate part + two lids, already on their hinges
PRINT_IN_PLACE_GAP = 0.35        # a body off the bed is accepted only if all its lowest faces rest this close above another body

# Design frame (as used): X left -> right seen from the front, 0 at the plate's left face; Y towards the
# rack, 0 = back face, loops at -Y, rack pins at +Y; Z along the cable, 0 = plate bottom end.
# build_part() turns it onto its back for printing (rack pin heads on the bed, lids on top):
# print X = X, print Y = Z, print Z = 4.75 - Y.

# --- back plate (the adaptor holder's pin column, pin sample height) ---
PLATE_W = 20.0                   # D1 plate width (X)
BACK_T = 4.0                     # D2 plate thickness (Y); also the loop base ("ears") thickness
PLATE_H = 54.0                   # D3 plate length (Z)

# --- keyhole pins (same as u-hook-adaptor-holder) ---
PIN_PITCH = 38.0                 # D4 pin pitch, centre to centre
LOWER_PIN_Z = 8.0                # D5 lower pin centre
PIN_X = 10.0                     # D7 pin centre X = PLATE_W / 2
NECK_D = 5.6                     # D8 groove width across (X)
NECK_L = 1.7                     # D9 groove width (Y)
HEAD_D = 9.6                     # D10 head width (X)
HEAD_T = 3.0                     # D11 head thickness (Y)

# --- cable loop: rounded U lid on a hinge, after the reference Deskcable organiser ---
LOOP_H = 12.0                    # D12 loop length along the cable (Z), centred on its pin
CAV_W = 35.2                     # D13 cable space width (X) = 40 - 2 x WALL
CAV_D = 12.0                     # D14 cable space depth (Y), base face to lid = reference 10 + 2
WALL = 2.4                       # D15 lid wall (6 lines of 0.4; reference 4-5)
R_OUT = 6.0                      # D17 lid outer corner radius
R_IN = 3.6                       # D18 lid inner corner radius = R_OUT - WALL
GAP = 0.3                        # D19 clearance between moving faces (reference 0.25-0.3)
POST_H = 5.0                     # D25 hinge and latch post height above the base (Y)

# --- 3-knuckle hinge along the cable: tongue on the base, lid knuckles each side, 45 deg cone pins ---
HINGE_W = 3.6                    # D37 hinge post / knuckle width (X)
KNUCKLE = 3.5                    # D35 lid knuckle length (Z), one at each end of the loop
CONE_D = 2.4                     # D33 cone pin base diameter, on each tongue face
CONE_L = 1.2                     # D34 cone pin length (45 deg)

# --- snap latch: skirt + barb on the lid's right leg, notch in the latch post ---
POST_W = 2.4                     # D24 latch post width (X)
SKIRT_T = 1.3                    # D26 lid skirt thickness (X), flexes over the post
BARB = 0.5                       # D27 barb depth (X); rides 0.2 over the post (BARB - GAP)

# --- weight-saving window, 3 mm from each loop ---
WIN_W = 12.0                     # D28 window width (X)
WIN_H = 20.0                     # D29 window length (Z)

# derived (not spec inputs)
PIN_ZS = (LOWER_PIN_Z, LOWER_PIN_Z + PIN_PITCH)
LOOP_Z0 = [z - LOOP_H / 2 for z in PIN_ZS]            # 2 and 40
LX0 = PIN_X - CAV_W / 2 - WALL                       # loop left face (-10)
LX1 = PIN_X + CAV_W / 2 + WALL                       # loop right face (30)
Y_BASE = -BACK_T                                     # base face (-4)
Y_POST = Y_BASE - POST_H                             # post tops (-9)
Y_FRONT = Y_BASE - CAV_D - WALL                      # lid front (-18.4)
HX = LX0 + HINGE_W / 2                               # hinge axis X (-8.2)
HY = Y_BASE - POST_H / 2                             # hinge axis Y (-6.5)
TONGUE = LOOP_H - 2 * (KNUCKLE + GAP)                # D36 tongue length (4.4)
PX1 = LX1 - SKIRT_T - GAP                            # latch post outer face (28.4)
WIN_Z0 = LOOP_Z0[0] + LOOP_H + 3.0                   # 17


def _to_print(p):
    """Design point -> print point (for probes)."""
    x, y, z = p
    return (x, z, 4.75 - y)


PROBES_INSIDE = [_to_print(p) for p in [
    (PIN_X, NECK_L / 2, LOWER_PIN_Z),                             # lower rack pin groove
    (PIN_X, NECK_L + HEAD_T / 2, LOWER_PIN_Z + PIN_PITCH),        # upper rack pin head
    (HX, HY, LOOP_Z0[0] + LOOP_H / 2),                            # hinge tongue, lower loop
    (HX + 0.3, HY, LOOP_Z0[1] + KNUCKLE / 2),                     # lid knuckle, upper loop
    (PIN_X, Y_FRONT + WALL / 2, LOOP_Z0[1] + LOOP_H / 2),         # lid front wall
    (PX1 - POST_W / 2, Y_POST + 0.5, LOOP_Z0[0] + 6),             # latch post
]]
PROBES_OUTSIDE = [_to_print(p) for p in [
    (PIN_X, -BACK_T / 2, WIN_Z0 + WIN_H / 2),                     # window
    (PIN_X, Y_BASE - CAV_D / 2, LOOP_Z0[0] + 6),                  # cable space
    (HX + 1.6, HY, LOOP_Z0[0] + KNUCKLE + GAP / 2),               # axial gap tongue / knuckle (beside the cone)
    (PIN_X, Y_BASE - GAP / 2 + 0.0, LOOP_Z0[0] + 6),              # nothing between base and cable space
]]
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
import math  # noqa: E402
from shapely.geometry import Point, Polygon, box as sbox  # noqa: E402  (shapely is part of the skill stack)
from shapely.ops import unary_union  # noqa: E402

RES = 48   # arc resolution for the 2D outlines


def _pin(z):
    """Keyhole pin along +Y: groove against the back face, then the head; both point-down teardrops."""
    neck = cad.rotate(cad.teardrop_hole(NECK_D, NECK_L + 1, axis="y", flat_top=False), y=180)
    head = cad.rotate(cad.teardrop_hole(HEAD_D, HEAD_T, axis="y", flat_top=False), y=180)
    neck = cad.translate(neck, y=(NECK_L + 1) / 2)
    head = cad.translate(head, y=HEAD_T / 2)
    neck = cad.translate(neck, x=PIN_X, y=-1, z=z)                 # 1 mm buried in the plate
    head = cad.translate(head, x=PIN_X, y=NECK_L, z=z)
    return cad.union(neck, head)


def _rr_front(x0, x1, y_back, y_front, r):
    """Rectangle x0..x1 x y_front..y_back with its two front corners (at y_front) rounded r."""
    s = unary_union([sbox(x0, y_front + r, x1, y_back), sbox(x0 + r, y_front, x1 - r, y_back),
                     Point(x0 + r, y_front + r).buffer(r, RES), Point(x1 - r, y_front + r).buffer(r, RES)])
    return s.intersection(sbox(x0, y_front, x1, y_back))


# ---------- 2D outlines in the design frame (X, Y), lid closed ----------
def _lid_body2d():
    """Rounded U strap: legs stop GAP above the posts; right leg carries the skirt and the barb."""
    u = _rr_front(LX0, LX1, Y_POST - GAP, Y_FRONT, R_OUT).difference(
        _rr_front(LX0 + WALL, LX1 - WALL, 1.0, Y_FRONT + WALL, R_IN))
    skirt = sbox(LX1 - SKIRT_T, Y_POST - GAP - 0.01, LX1, Y_BASE - GAP)
    yr = HY                                                    # barb's retaining face
    barb = Polygon([(LX1 - SKIRT_T - BARB, yr), (LX1 - SKIRT_T + 0.01, yr),
                    (LX1 - SKIRT_T + 0.01, yr + BARB + 0.01)])  # 45 deg ramp faces the base
    return unary_union([u, skirt, barb])


def _knuckle2d():
    """Lid knuckle over the base, rounded about the axis where it swings towards the base."""
    k = sbox(LX0, Y_POST - GAP - 0.01, LX0 + HINGE_W, Y_BASE - GAP)
    r_k = (Y_BASE - HY) - GAP                                  # 2.2: clears the base face when it turns
    upper_left = sbox(LX0 - 1, HY, HX, Y_BASE).difference(Point(HX, HY).buffer(r_k, RES))
    return k.difference(upper_left)


def _tongue2d():
    """Hinge tongue on the base, rounded below the axis so the lid can turn round it."""
    post = sbox(LX0, Y_POST, LX0 + HINGE_W, Y_BASE + 0.1)
    keep = unary_union([Point(HX, HY).buffer((Y_BASE - HY) - GAP, RES), sbox(LX0 - 1, HY, LX0 + HINGE_W + 1, 1)])
    return post.intersection(keep)


def _latch_post2d():
    post = sbox(PX1 - POST_W, Y_POST, PX1, Y_BASE + 0.1)
    notch = sbox(LX1 - SKIRT_T - BARB - GAP, HY - GAP, PX1 + 0.1, HY + BARB + GAP)
    return post.difference(notch)


# ---------- solids in the design frame ----------
def _cone(z_face, up):
    """45 deg cone pin on a tongue face, pointing along +Z (up) or -Z."""
    c = cad.cylinder(CONE_D, CONE_L - 0.1, d_top=0.2)
    if not up:
        c = cad.rotate(c, x=180)
    return cad.translate(c, x=HX, y=HY, z=z_face + (-0.01 if up else 0.01))


def _socket(z_face, up):
    """Cone socket in a knuckle face: the pin cone grown by GAP normal to its surface."""
    r0 = CONE_D / 2 - GAP + GAP * math.sqrt(2)                 # radius at the knuckle face
    s = cad.cylinder(2 * r0, r0, d_top=0.01)
    s = cad.translate(s, z=-0.01)
    if not up:
        s = cad.rotate(s, x=180)
    return cad.translate(s, x=HX, y=HY, z=z_face)


def _lid(z0):
    """One lid, closed, loop band from z0: knuckle | tongue clearance | knuckle, sockets for the cones."""
    zt0, zt1 = z0 + KNUCKLE + GAP, z0 + LOOP_H - KNUCKLE - GAP          # tongue zone
    r_clear = math.hypot(HINGE_W / 2, Y_BASE - HY) + GAP                 # tongue corners + GAP
    kn = unary_union([_lid_body2d(), _knuckle2d()])
    mid = _lid_body2d().difference(unary_union([Point(HX, HY).buffer(r_clear, RES),
                                                 sbox(LX0 - 1, HY - r_clear, LX0 + HINGE_W, 1)]))
    lid = cad.union(cad.extrude(kn, KNUCKLE, z0=z0),
                    cad.extrude(mid, zt1 - zt0 + 2 * GAP, z0=zt0 - GAP),
                    cad.extrude(kn, KNUCKLE, z0=zt1 + GAP))
    return cad.difference(lid, _socket(zt0 - GAP, up=False), _socket(zt1 + GAP, up=True))


def _loop_base(z0):
    zt0, zt1 = z0 + KNUCKLE + GAP, z0 + LOOP_H - KNUCKLE - GAP
    ear = cad.extrude(sbox(LX0, Y_BASE, LX1, 0.0), LOOP_H, z0=z0)
    tongue = cad.extrude(_tongue2d(), zt1 - zt0, z0=zt0)
    post = cad.extrude(_latch_post2d(), LOOP_H, z0=z0)
    return cad.union(ear, tongue, post, _cone(zt1, up=True), _cone(zt0, up=False))


def _base():
    plate = cad.translate(cad.box(PLATE_W, BACK_T, PLATE_H, center_xy=False), y=-BACK_T)
    win = cad.translate2d(cad.rounded_rect(WIN_W, WIN_H, WIN_W / 2 - 0.01), PIN_X, WIN_Z0 + WIN_H / 2)
    cut = cad.translate(cad.rotate(cad.extrude(win, BACK_T + 2), x=90), y=1)       # (X, Z) profile, through Y
    base = cad.union(plate, *[_loop_base(z0) for z0 in LOOP_Z0], *[_pin(z) for z in PIN_ZS])
    return cad.difference(base, cut)


def design(lid_angle=0.0):
    """Plate part and both lids in the design frame; lid_angle opens the lids (degrees)."""
    lids = []
    for z0 in LOOP_Z0:
        lid = _lid(z0)
        if lid_angle:
            lid = cad.translate(cad.rotate(cad.translate(lid, x=-HX, y=-HY), z=-lid_angle), x=HX, y=HY)
        lids.append(lid)
    return _base(), lids


def _print_in_place(check):
    """printcheck's on_bed rule fails every body that does not touch the bed. A print-in-place lid
    never does: like the reference, it rests GAP above the base. Accept such a body only when every
    one of its lowest downward faces has another body at most PRINT_IN_PLACE_GAP below it; anything
    else (a truly loose piece) still fails."""
    import numpy as np

    def wrapped(mesh, *a, **kw):
        res = check(mesh, *a, **kw)
        c = res.get("on_bed")
        floating = (c.data or {}).get("floating_bodies") if c else None
        if not c or c.status != printcheck.FAIL or not floating or c.data.get("min_z", 1) != 0.0:
            return res
        faces = np.asarray(mesh.faces)
        labels = printcheck._components(faces, len(mesh.vertices))
        tris = np.asarray(mesh.triangles, dtype=float)
        nz = mesh.face_normals[:, 2]
        report = []
        for b in floating:
            own = labels == b
            zb = tris[own][:, :, 2].min()
            low = own & (nz < -0.999) & (tris[:, :, 2].max(axis=1) <= zb + 0.01)
            others = tris[~own]
            org = mesh.triangles_center[low] - np.array([0, 0, 1e-3])
            dirs = np.tile([0.0, 0.0, -1.0], (len(org), 1))
            d = printcheck._first_hits(org, dirs, others) + 1e-3
            ok = bool(len(d)) and bool(np.all(d <= PRINT_IN_PLACE_GAP))
            report.append({"body": int(b), "lowest_z": round(float(zb), 3), "faces": int(low.sum()),
                           "max_gap": round(float(np.max(d)), 3) if len(d) else None, "ok": ok})
        if all(x["ok"] for x in report):
            i = res.checks.index(c)
            res.checks[i] = printcheck.Check(
                "on_bed", printcheck.WARN,
                f"{c.data['contact_area_mm2']:.1f} mm2 on the bed; print in place: {len(report)} lid(s) rest "
                f"{max(x['max_gap'] for x in report):.2f} mm above the base (all lowest faces checked)",
                dict(c.data, print_in_place=report))
        return res
    return wrapped


printcheck.check_printable = _print_in_place(printcheck.check_printable)


def build_part():
    """Print in place, on its back: rack pin heads on the bed, lids on top, hinges already fitted."""
    base, lids = design()
    part = cad.rotate(cad.union(base, *lids), x=-90)          # (x, y, z) -> (x, z, -y)
    return cad.drop_to_bed(part)
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
