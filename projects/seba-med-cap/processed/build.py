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
NAME = "seba-med-cap"            # output stem; parts become seba-med-cap-base / -lid
MATERIAL = "PETG"                # spec print.material (primary since rev 5; PLA released too)
COLOR = {"base": "#4f8cff", "lid": "#7fb0ff"}  # preview colours only

PRINTER_BED = (220, 220, 250)    # spec print.printer_bed
NOZZLE = 0.4                     # spec print.nozzle
LAYER = 0.2                      # spec print.layer
OVERHANG_LIMIT = 45              # the snap lip ramp is exactly 45 degrees
SUPPORTS_ALLOWED = False         # spec print.supports
EXPECTED_BODIES = 1              # one solid per part

# --- bottle neck (measured / accepted) ---
BEAD_D = 20.8                    # D3 neck bead OD (measured, user caliper)
TOP_TO_BEAD = 7.0                # D4 neck top to bead underside (photo estimate, accepted by user)
BORE_D = 8.8                     # D5 neck bore ID (measured, user caliper)
TOP_TO_LUG = 9.4                 # D6 neck top to shoulder lug top (photo estimate, accepted by user)

# --- base ---
CAP_OD = 46.1                    # D7 cap OD, same as the original (measured)
DECK_T = 2.0                     # D9 deck thickness, 10 layers
SLEEVE_WALL = 1.6                # D10 snap sleeve wall, 4 perimeters
SKIRT_WALL = 1.6                 # D11 skirt wall, 4 perimeters
LUG_CLEAR = 0.5                  # D12 skirt edge stays this far above the lug
SNAP_UNDERCUT = 0.35             # D14 lip overlaps the bead by this per side (PLA-friendly)
LIP_H = 0.4                      # D15 straight land of the lip, 2 layers
SLOT_N = 6                       # D16 flex slots in the sleeve
SLOT_W = 1.2                     # D17 slot width, 3 x nozzle
SLOT_L = 5.0                     # D18 slot length from the sleeve rim
CHANNEL_D = 5.0                  # D19 dispensing channel (rev 4: 4.0 -> 5.0, user)
SPOUT_WALL = 1.2                 # D46 spout ring wall around the channel, 3 x nozzle (rev 4)
GROOVE_W = 1.6                   # D47 groove around the spout, radial width (rev 4)
GROOVE_DEPTH = 1.0               # D48 groove depth into the deck; 1.0 deck stays under it (rev 4)
RING_FIT = FITS["snug"]          # lid ring bore on the spout OD, per side: the click seal
RING_OUT_GAP = 0.2               # lid ring outer face to the groove outer wall, per side
RING_H = 0.8                     # D49 lid ring height: groove depth - 0.2 clearance
RING_LEAD = 0.2                  # lead-in chamfer on the lid ring bore tip
SEAL_L = 4.0                     # D20 seal tube length into the neck bore (rev 5: 3.0 -> 4.0, stops the wobble)
FOOT_CHAMFER = 0.4               # D26 elephant-foot chamfer on bed edges
SKIRT_EXT = 8.0                  # D43 skirt extension (rev 5: 6.2 + measured remaining gap 1.8 = touches the shoulder)
SKIRT_BEVEL = 1.0                # D44 skirt rim bevel, inner edge higher: follows the ~32 deg shoulder slope
TIP_CHAMFER = 0.4                # lead-in on the seal tube tip and pin tip (2 layers)
BORE_CLEAR = FITS["free"]        # sleeve bore over the bead
SEAL_FIT = FITS["snug"]          # seal tube in the neck bore

# --- lid ---
LID_T = 2.0                      # D21 lid disc thickness
PIN_L = 3.0                      # D22 plug length (rev 6: 1.6 -> 3.0); the arc shifts the tip only ~0.06
PLUG_SHANK_CLEAR = 0.05          # D50 plug shank clearance per side at the root (shank 4.9 in 5.0)
PLUG_BULB_D = 5.0                # D51 plug bulb OD (rev 8: 5.2 still tight; the print adds ~0.1/side, which gives the click)
PLUG_BULB_Z = 1.2                # D54 bulb land starts this far from the lid face (= depth in the channel)
PLUG_BULB_LAND = 0.4             # bulb straight land, 2 layers
PLUG_TIP_D = 4.5                 # D52 plug tip OD: lead-in taper 5.3 -> 4.5 over the last 1.4 mm
PLUG_WALL = 1.0                  # D53 hollow plug wall at the shank: it flexes in and seals
CH_GROOVE_D = 5.2                # D55 groove in the channel that the bulb clicks into (bulb stays 0.05/side squeezed)
TAB_OUT = 6.0                    # D23 thumb tab protrusion beyond the disc
TAB_W = 12.0                     # D24 thumb tab width
TAB_R = 2.0                      # thumb tab corner radius
LID_OFFSET_X = 60.0              # D25 lid centre from base centre (layout, clears the hinge side)

# --- hinge (clip-on pin hinge, -X side) ---
PIN_HINGE_D = 3.0                # D30 hinge pin diameter
HINGE_OFF = 3.3                  # D31 hinge axis outside the skirt (clip radius 2.9 + 0.4)
PIN_FLAT = 0.45                  # D32 pin flat on the bed: cut at the 45 deg point, r(1 - cos45) = 0.44
HINGE_GAP = 8.0                  # D33 gap between the knuckles
KNUCKLE_W = 4.0                  # D34 knuckle width each
KNUCKLE_H = 4.0                  # D42 knuckle depth below the top face
CLIP_WALL = 1.2                  # D35 C-clip ring wall
CLIP_FIT = FITS["sliding"]       # clip bore clearance on the pin, per side
CLIP_SIDE = FITS["free"]         # clip clearance to each knuckle
CLIP_HORN_CAP = 0.3              # clip ring cut flat this far above its bore top: no knife-edge horn tips

# --- latch (+X side) ---
LATCH_W = 8.0                    # D37 latch width
LATCH_DEPTH = 0.5                # D38 bead height = hook overlap (rev 5 PETG 0.5, strain 3.0 %; PLA 0.4 via material_values)
LATCH_Z = 4.0                    # D39 bead apex below the top face
LATCH_ARM_T = 1.0                # D40 latch arm thickness
LATCH_GAP = 0.2                  # D41 arm clearance to the bead apex
LATCH_PRELOAD = 0.2              # D45 hook sits this much closer to the lid: pulls the lid down (rev 5 PETG 0.2; PLA 0.15)

_R = CAP_OD / 2
_XA = -(_R + HINGE_OFF)                       # hinge axis X
_ZA_LID = LID_T + PIN_HINGE_D / 2 - PIN_FLAT  # hinge axis height in the lid print frame
PROBES_INSIDE = {
    "base": [(15.0, 0.0, 1.0), (_R - SKIRT_WALL / 2, 0.0, 6.0),
             (BEAD_D / 2 + BORE_CLEAR + SLEEVE_WALL / 2, 0.0, 6.0), (3.2, 0.0, 4.0),
             (_XA, 0.0, 0.8), (_R + 0.1, 0.0, LATCH_Z),
             (_R - SKIRT_WALL / 2, 0.0, 15.0), (3.1, 0.0, 0.5)],
    "lid": [(LID_OFFSET_X + 15.0, 0.0, 1.0), (LID_OFFSET_X + 2.0, 0.0, LID_T + 1.0),
            (LID_OFFSET_X + 2.45, 0.0, LID_T + PLUG_BULB_Z + 0.2),
            (LID_OFFSET_X + _XA - 2.3, 0.0, _ZA_LID), (LID_OFFSET_X + 4.4, 0.0, LID_T + 0.4),
            (LID_OFFSET_X + _R + LATCH_DEPTH + LATCH_GAP + 0.5, 0.0, LID_T + 2.0)],
}
PROBES_OUTSIDE = {
    "base": [(0.0, 0.0, 1.0), (0.0, 0.0, 4.0), (4.5, 0.0, 0.5), (8.0, 0.0, 6.0), (17.0, 0.0, 6.0), (_XA, 0.0, 3.5)],
    "lid": [(LID_OFFSET_X + 10.0, 0.0, LID_T + 2.0), (LID_OFFSET_X, 0.0, LID_T + 1.0), (LID_OFFSET_X + _XA, 0.0, _ZA_LID),
            (LID_OFFSET_X + _XA, 0.0, _ZA_LID + 2.5), (LID_OFFSET_X + _R + 0.2, 0.0, LID_T + 1.0)],
}
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
SEG = 180  # revolve segments: chord ~0.8 mm on the 46 mm skirt, flats within 0.01 mm


def base_profile():
    """Half cross-section (r, z) of the base, revolved about Z. z = 0 is the cap top face."""
    r_cap = CAP_OD / 2
    r_skirt_in = r_cap - SKIRT_WALL
    r_bore = BEAD_D / 2 + BORE_CLEAR
    r_lip = BEAD_D / 2 - SNAP_UNDERCUT
    r_sleeve = r_bore + SLEEVE_WALL
    r_seal = BORE_D / 2 - SEAL_FIT
    step = r_bore - r_lip                       # 45 degree ramp and lead-in
    h = DECK_T + TOP_TO_LUG - LUG_CLEAR + SKIRT_EXT  # D13 skirt height (outer edge)
    z_bead = DECK_T + TOP_TO_BEAD               # bead underside when seated
    z_end = z_bead + step + LIP_H + step        # sleeve rim
    z_seal = DECK_T + SEAL_L
    return [
        (0.0, 0.0), (r_cap - FOOT_CHAMFER, 0.0), (r_cap, FOOT_CHAMFER), (r_cap, h),
        (r_skirt_in, h - SKIRT_BEVEL), (r_skirt_in, DECK_T),
        (r_sleeve, DECK_T), (r_sleeve, z_end), (r_bore, z_end),
        (r_lip, z_end - step), (r_lip, z_bead + step), (r_bore, z_bead),
        (r_bore, DECK_T), (r_seal, DECK_T), (r_seal, z_seal - TIP_CHAMFER),
        (r_seal - TIP_CHAMFER, z_seal), (0.0, z_seal),
    ], r_bore, r_sleeve, z_end


def _profile_y(points, width):
    """Solid from an XZ profile (given as (x, z) pairs), extruded along Y, centred on y = 0."""
    return cad.stand_up(cad.extrude(cad.Polygon(points), width))


def _rod_y(d, length, x, z):
    """Cylinder along Y, centred on y = 0, axis at (x, z)."""
    rod = cad.rotate(cad.translate(cad.cylinder(d, length, n=SEG // 2), z=-length / 2), x=90)
    return cad.translate(rod, x=x, z=z)


def build_base():
    pts, r_bore, r_sleeve, z_end = base_profile()
    h = DECK_T + TOP_TO_LUG - LUG_CLEAR + SKIRT_EXT
    body = cad.m3.Manifold.revolve(cad.cross_section(cad.Polygon(pts)), SEG)
    # hinge: two knuckles joined by a pin along Y; the pin is cut flat at z = 0 (the bed)
    r_pin = PIN_HINGE_D / 2
    z_axis = r_pin - PIN_FLAT
    x_out = _XA - r_pin - CLIP_WALL
    x_in = -(_R - SKIRT_WALL - 1.0)
    knuckle = cad.translate(cad.box(x_in - x_out, KNUCKLE_W, KNUCKLE_H, center_xy=False),
                            x=x_out, y=HINGE_GAP / 2)
    knuckles = cad.union(knuckle, cad.mirror(knuckle, "y"))
    pin = cad.intersection(_rod_y(PIN_HINGE_D, HINGE_GAP + 1.0, _XA, z_axis),
                           cad.translate(cad.box(4 * r_pin, HINGE_GAP + 2.0, 2 * r_pin), x=_XA))
    r_cav = _R - SKIRT_WALL
    cavity = cad.m3.Manifold.revolve(cad.cross_section(cad.Polygon(
        [(0.0, DECK_T), (r_cav, DECK_T), (r_cav, h + 1.0), (0.0, h + 1.0)])), SEG)  # same facets as the skirt
    hinge = cad.difference(cad.union(knuckles, pin), cavity)
    # latch bead: 45 degree faces both sides, apex LATCH_DEPTH outside the skirt
    e = 0.6
    bead = _profile_y([(_R - e, LATCH_Z - LATCH_DEPTH - e), (_R + LATCH_DEPTH, LATCH_Z),
                       (_R - e, LATCH_Z + LATCH_DEPTH + e)], LATCH_W)
    channel = cad.hole(CHANNEL_D, DECK_T + SEAL_L, DECK_T + SEAL_L, foot=FOOT_CHAMFER)
    # click groove inside the channel: 45 degree faces both sides, matches the lid plug bulb
    r_ch = CHANNEL_D / 2
    dg = CH_GROOVE_D / 2 - r_ch
    g0 = PLUG_BULB_Z - dg - 0.05
    # the groove must reach past where the plug's lead-in taper drops back to the channel radius,
    # or the plug stays squeezed when the lid is shut (rev 8, found by the closing sweep)
    slope = (PLUG_BULB_D - PLUG_TIP_D) / 2 / (PIN_L - PLUG_BULB_Z - PLUG_BULB_LAND)
    h_exit = PLUG_BULB_Z + PLUG_BULB_LAND + max(0.0, PLUG_BULB_D / 2 - r_ch) / slope
    g1 = h_exit + dg + 0.1
    ch_groove = cad.m3.Manifold.revolve(cad.cross_section(cad.Polygon([
        (r_ch - 0.2, g0), (r_ch, g0), (r_ch + dg, g0 + dg), (r_ch + dg, g1 - dg), (r_ch, g1), (r_ch - 0.2, g1)])), SEG)
    channel = cad.union(channel, ch_groove)
    slot_len = r_sleeve - r_bore + 1.0
    slot = cad.translate(cad.box(slot_len, SLOT_W, SLOT_L + 1.0), x=(r_bore + r_sleeve) / 2, z=z_end - SLOT_L)
    slots = [cad.rotate(slot, z=360.0 / SLOT_N * (i + 0.5)) for i in range(SLOT_N)]
    # spout: an annular groove in the top face leaves a ring standing round the channel, flush with the deck
    r_spout = CHANNEL_D / 2 + SPOUT_WALL
    groove = cad.difference(cad.translate(cad.cylinder(2 * (r_spout + GROOVE_W), GROOVE_DEPTH + 1.0, n=SEG), z=-1.0),
                            cad.translate(cad.cylinder(2 * r_spout, GROOVE_DEPTH + 3.0, n=SEG), z=-2.0))
    return cad.difference(cad.union(body, hinge, bead), channel, groove, *slots)


def build_lid():
    """Lid in print orientation: outer face on the bed (z = 0), inner face at z = LID_T."""
    outline = cad.circle2d(CAP_OD, n=SEG).union(
        cad.translate2d(cad.rounded_rect(_R + TAB_OUT, TAB_W, TAB_R), x=(_R + TAB_OUT) / 2))
    disc = cad.chamfered_extrude(outline, LID_T, bottom=FOOT_CHAMFER)
    # hollow channel plug (rev 6): shank, 45 degree step out to the bulb, land, long lead-in taper to the tip
    r_sh = CHANNEL_D / 2 - PLUG_SHANK_CLEAR
    r_b = PLUG_BULB_D / 2
    r_in = r_sh - PLUG_WALL
    z_step = PLUG_BULB_Z - (r_b - r_sh)
    plug = cad.translate(cad.m3.Manifold.revolve(cad.cross_section(cad.Polygon([
        (r_in, -0.01), (r_sh, -0.01), (r_sh, z_step), (r_b, PLUG_BULB_Z), (r_b, PLUG_BULB_Z + PLUG_BULB_LAND),
        (PLUG_TIP_D / 2, PIN_L), (r_in, PIN_L)])), SEG), z=LID_T)
    # seal ring: drops into the base groove and grips the spout OD (rev 4)
    r_spout = CHANNEL_D / 2 + SPOUT_WALL
    ring_in = r_spout + RING_FIT
    ring_out = r_spout + GROOVE_W - RING_OUT_GAP
    ring = cad.m3.Manifold.revolve(cad.cross_section(cad.Polygon([
        (ring_in, LID_T - 0.01), (ring_out, LID_T - 0.01), (ring_out, LID_T + RING_H),
        (ring_in + RING_LEAD, LID_T + RING_H), (ring_in, LID_T + RING_H - RING_LEAD)])), SEG)
    plug = cad.union(plug, ring)
    # hinge C-clip: ring around the pin axis, 45 degree mouth facing up (towards the bottle when closed)
    r_in = PIN_HINGE_D / 2 + CLIP_FIT
    r_out = r_in + CLIP_WALL
    clip_w = HINGE_GAP - 2 * CLIP_SIDE
    mouth = 2 * r_in * 0.7071067811865476
    tab = cad.translate(cad.box(-(_XA - r_out) - (_R - 2.0), clip_w, LID_T, center_xy=False),
                        x=_XA - r_out, y=-clip_w / 2)
    ring = _rod_y(2 * r_out, clip_w, _XA, _ZA_LID)
    bore = _rod_y(2 * r_in, clip_w + 1.0, _XA, _ZA_LID)
    mouth_cut = cad.translate(cad.box(mouth, clip_w + 1.0, r_out + 1.0), x=_XA, z=_ZA_LID)
    clip = cad.difference(cad.union(tab, ring), bore, mouth_cut)
    # flatten the clip horns: the mouth cut leaves knife-edge tips near the outer radius
    horn_top = _ZA_LID + r_in + CLIP_HORN_CAP
    clip = cad.intersection(clip, cad.box(4 * CAP_OD, 4 * CAP_OD, horn_top))
    # latch arm with a 45 degree hook that catches under the base bead
    x_face = _R + LATCH_DEPTH + LATCH_GAP          # arm inner face, clear of the bead apex
    hook = x_face - _R                              # hook reaches in to the skirt radius
    z_apex = LID_T + LATCH_Z + LATCH_DEPTH - LATCH_PRELOAD  # hook apex just inside the bead's lower 45 degree face
    arm = _profile_y([(x_face, LID_T - 0.01), (x_face + LATCH_ARM_T, LID_T - 0.01),
                      (x_face + LATCH_ARM_T, z_apex + hook), (x_face, z_apex + hook),
                      (_R, z_apex), (x_face, z_apex - hook)], LATCH_W)
    return cad.translate(cad.union(disc, plug, clip, arm), x=LID_OFFSET_X)


def build_part():
    return {"base": build_base(), "lid": build_lid()}


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
