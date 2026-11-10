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
NAME = "music-stand-plate"          # output file stem: a-z, 0-9 and dashes only
MATERIAL = "PLA"                 # from intake; sets density for the mass estimate
COLOR = {"nut": "#c9a227", "v-tab": "#e07a5f", "bolt-1": "#9aa0a6", "bolt-2": "#9aa0a6", "jam-nut-1": "#9aa0a6", "jam-nut-2": "#9aa0a6", "centre": "#f5c896", "extender-left": "#aacdeb", "extender-right": "#aae1b4"}  # viewer only

PRINTER_BED = (180, 180, 180)    # A1 mini build volume (A1)
NOZZLE = 0.4                     # nozzle diameter; minimum wall = 2 x NOZZLE
LAYER = 0.2                      # layer height
OVERHANG_LIMIT = 60              # 60 for the thread flanks (~51 deg) and the V's gable relief (~58 deg); the 3 big plates pass at 45
SUPPORTS_ALLOWED = False         # no supports
EXPECTED_BODIES = 1              # each part is one solid

# --- holder (the existing stand), from the user's calipers and sketch ---
CH_LEN = 66.4                    # D1 channel length (photos 66.4 / 66.2; sketch 66.9, Q2)
CH_IN_TOP = 37.6                 # D2 inner width at the open top end (sketch 115004)
CH_IN_BOT = 30.6                 # D3 inner width at the bottom end (sketch 115004)
CH_DEPTH = 9.5                   # D6 usable channel depth (sketch 115004; tab is 4 mm)
CH_STOP_H = 1.0                  # D8 bottom curved support height (sketch 115004)
STUD_POS = 9.5                   # D9 stud centre from the channel top (fit test marks 9.7 / 10.7, photo 131610 9.2)
STUD_D = 5.9                     # D10 stud diameter (caliper 5.9, photo 130155): M6 thread
DOME1_POS = 36.3                 # D11 dome rivet 1 from the channel top (photo 131610, ruler)
DOME2_POS = 57.8                 # D12 dome rivet 2 from the channel top (photo 131610, ruler)
DOME_D = 9.5                     # D13 dome head diameter (photo 131610)
COLLAR_D = 6.4                   # D54 raised collar around the stud hole (photo 131610): the slot clears this, not just the stud
DOME_H = 2.0                     # D14 dome head height (estimated)

# --- tab ---
TAB_WIDEN = 1.0                  # D62 tab made this much wider per side after the fit test (user: snugger fit)
TAB_L = 65.0                     # D16 tab length below the plate (plate rests on the channel top; tip stops 0.4 short of the support)
TAB_T = 4.0                      # D17 tab thickness (= plate): the stud must come through for the nut
TAB_LEADIN = 2.0                 # D44 45 deg chamfer on the back edge of the tab tip (easier entry)
STUD_SLOT_EXTRA = 1.0            # D52 stud slot = collar diameter + this (0.5 mm per side) -> 7.4 mm
BRIDGE_L = 5.0                   # D56 the slot is closed by a bridge this long at the tab tip (joins the two legs)
BRIDGE_RELIEF = 4.0              # D57 peak height of the gable relief under the bridge (back face): rides over collar and domes
RELIEF_W = 13.0                  # D61 relief width at the back face (gable faces about 58 deg from vertical, no flat roof)
TIP_BOSS_T = 7.0                 # D58 tab thickness at the tip boss (3 mm of bridge over the 4 mm relief peak; 2.5 mm free in the 9.5 mm channel)
TIP_BOSS_W = 15.0                # D59 boss width, centred (clear of the channel's side lips)
TIP_BOSS_L = 8.0                 # D60 boss length from the tip
SLOT_OVERRUN = 1.0               # D55 both slot ends run this much further towards the plate than the measured feature
DOME_SLOT_EXTRA = 1.5            # D53 dome slot = dome diameter + this
NUT_RECESS_D = 17.0              # D50 recess in the tab front around the stud, so the nut sits lower
NUT_RECESS_DEPTH = 2.0           # D51 recess depth (2 mm of tab left under the nut, more stud thread for the nut)

# --- printed M6 thumb nut (test) ---
THREAD_D = 6.0                   # M6 major diameter (stud measured 5.9)
THREAD_P = 1.0                   # D47 M6 coarse pitch (assumed: standard for M6)
NUT_OD = 16.0                    # D48 thumb nut outside diameter
NUT_H = 8.0                      # D49 thumb nut height (8 turns of thread)
NUT_GRIP_N = 10                  # grip notches around the nut
NUT_GRIP_D = 3.0                 # notch diameter
NUT_POS = (60.0, 262.0)          # where the thumb nut sits in the model files (next to the V)
THREAD_CLEAR = FITS["sliding"]   # radial clearance on the printed internal thread (metal stud in PLA)

# --- plate ---
PLATE_T = 4.0                    # D18 plate thickness
PLATE_W = 170.0                  # D19 centre plate width
PLATE_H = 170.0                  # D20 centre plate height (rev 12: the V is a separate part, so the full 170 the bed allows)
LIP_H = 10.0                     # D21 bottom lip projection towards the music
LIP_T = 4.0                      # D22 bottom lip thickness
OVERLAP = 40.0                   # D23 extender strip length behind the centre plate
EXT_VIS_W = 130.0                 # D24 extender width beyond the centre plate edge
EXT_T = 8.0                      # D25 extender main thickness (4 behind + 4 in the plate plane)
REBATE_D = 4.0                   # D26 rebate depth for the centre plate edge
EXT_H = 170.0                    # D27 extender height (= D20)
CORNER_R = 3.0                   # D33 outer corner radius
FOOT_CHAMFER = 0.4               # bottom edge chamfer that hides elephant foot

# --- vertical dovetail rails (extender) and grooves (centre plate): the extender drops on from the top ---
RAIL_NECK = 5.0                  # D37 rail width at its base (narrow neck)
RAIL_HEAD = 8.0                  # D38 rail width at its top (the dovetail head, 45 deg or less overhang)
RAIL_H = 2.4                     # D39 rail height above the strip face (groove depth is this + clearance)
RAIL_EDGE0 = 10.0                # D40 first rail centre from the centre plate side edge
RAIL_PITCH = 20.0                # D41 second rail this much further in (rails 10 and 30 from the edge)
RAIL_Y0 = 8.0                    # D42 rail bottom end = closed bottom end of the groove (the extender rests here)
RAIL_TOP_GAP = 8.0               # D43 the rail stops this far below the extender top edge

# --- hex mesh in the extenders ---
MESH_AF = 12.0                   # D34 hexagon across flats
MESH_RIB = 3.0                   # D35 rib width between holes
MESH_BORDER = 8.0                # D36 solid border around the mesh

# --- V tab as a separate part (rev 12): tongue behind the centre plate, 2 dovetail keys, 2 printed M6 bolts ---
TONGUE_L = 50.0                  # D63 tongue length above the V (sits behind the centre plate)
TONGUE_W = 44.0                  # D64 tongue width
KEY_X = 13.0                     # D65 the two dovetail keys on the tongue front, at x = +-13
KEY_END = 2.0                    # keys run from 2 mm above the V root to 2 mm below the tongue top
BOLT_Y1 = 15.0                   # D66 lower bolt, centre line, mm above the plate bottom edge
BOLT_Y2 = 38.0                   # D67 upper bolt
BOLT_L = 10.0                    # D68 printed M6 countersunk bolt, overall length (head in the plate)
BOLT_HEAD_D = 12.0               # D69 countersunk head diameter (90 deg, ISO 10642 size)
BOLT_HEX = 4.0                   # D73 hex key socket in the bolt head, across flats
BOLT_CLEAR = FITS["sliding"]     # printed bolt thread made this much smaller per side
BOLT_HOLE_CLEAR = FITS["free"]   # clearance hole for the bolt shank, per side
JAM_AF = 10.0                    # D70 printed M6 nut across flats
JAM_T = 3.2                      # D71 printed M6 nut thickness (thin "jam" nut)
JAM_POCKET = 2.0                 # D72 hex pocket depth in the back of the tongue (nut stops turning)
JAM_CLEAR = FITS["snug"]         # hex pocket clearance per side
TAB_SHIFT_Y = 245.0              # the V sits above the centre plate in the model files
SMALL_POS = {"bolt-1": (50.0, 200.0), "bolt-2": (50.0, 225.0), "jam-nut-1": (72.0, 200.0), "jam-nut-2": (72.0, 225.0)}

# --- model layout ---
LAYOUT_SHIFT = 50.0              # extenders are moved this far out in the model files (print layout, 10 mm gaps)

# --- fits (per side) ---
TAB_CLEAR = FITS["free"]         # tab in the channel: slightly loose, the nut tightens it
RAIL_CLEAR = FITS["sliding"]     # groove is the rail + this per side, so the extender drops on under its own weight
REBATE_CLEAR = FITS["sliding"]   # side gap between the centre plate edge and the rebate wall

# probes per part: points that must be solid / empty (x, y, z in the part's print position)
PROBES_INSIDE = {
    "centre": [(0.0, 50.0, 2.0), (0.0, 26.0, 3.0), (13.0, 30.0, 3.5), (60.0, 60.0, 2.0), (75.0, 60.0, 3.6), (0.0, 2.0, 8.0)],
    "v-tab": [(-10.0, 195.0, 2.0), (0.0, 275.0, 2.0), (13.0, 270.0, 5.5), (0.0, 182.5, 4.5), (0.0, 182.5, 5.8)],
    "bolt-1": [(54.0, 200.0, 1.0), (50.0, 200.0, 6.0)],
    "bolt-2": [(54.0, 225.0, 1.0), (50.0, 225.0, 6.0)],
    "jam-nut-1": [(76.2, 200.0, 1.6)],
    "jam-nut-2": [(76.2, 225.0, 1.6)],
    "nut": [(66.18, 264.01, 4.0)],
    "extender-right": [(115.0, 60.0, 2.0), (125.0, 60.0, 5.0)],
    "extender-left": [(-115.0, 60.0, 2.0), (-125.0, 60.0, 5.0)],
}
PROBES_OUTSIDE = {
    "centre": [(0.0, 15.0, 2.0), (0.0, 15.0, 3.8), (13.0, 30.0, 1.0), (75.0, 60.0, 1.0), (55.0, 60.0, 1.0)],
    "v-tab": [(0.0, 225.0, 2.0), (0.0, 195.0, 2.0), (0.0, 260.0, 3.0), (0.0, 260.0, 1.0), (8.0, 235.0, 3.5),
              (0.0, 182.5, 1.5), (0.0, 300.0, 2.0)],
    "bolt-1": [(50.0, 200.0, 11.0), (55.5, 200.0, 1.0), (50.0, 200.0, 0.5)],
    "bolt-2": [(50.0, 225.0, 11.0), (55.5, 225.0, 1.0), (50.0, 225.0, 0.5)],
    "jam-nut-1": [(72.0, 200.0, 1.6)],
    "jam-nut-2": [(72.0, 225.0, 1.6)],
    "nut": [(60.0, 262.0, 4.0)],
    "extender-right": [(115.0, 60.0, 6.0)],
    "extender-left": [(-115.0, 60.0, 6.0)],
}
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
import math  # noqa: E402


def _top_rounded(x_centre, w, h_top):
    """Rectangle of width w whose top corners (y = h_top) are rounded; bottom corners square."""
    r = cad.rounded_rect(w, h_top + 40.0, CORNER_R)
    return cad.translate2d(r, x=x_centre, y=h_top - (h_top + 40.0) / 2)


def _channel_inner(p):
    """Channel inner width at distance p from the open top end (linear taper D2 -> D3)."""
    return CH_IN_TOP - (CH_IN_TOP - CH_IN_BOT) * p / CH_LEN


def _tab_outline():
    p_tip = CH_LEN - CH_STOP_H                # tab tip rests on the curved support
    p_root = p_tip - TAB_L
    w_root = _channel_inner(p_root) - 2 * TAB_CLEAR + 2 * TAB_WIDEN
    w_tip = _channel_inner(p_tip) - 2 * TAB_CLEAR + 2 * TAB_WIDEN
    tab = cad.Polygon([(-w_root / 2, 0.5), (w_root / 2, 0.5), (w_tip / 2, -TAB_L), (-w_tip / 2, -TAB_L)])
    tab = tab.union(cad.box2d(-w_root / 2, 0.0, w_root / 2, 1.0))   # overlap into the plate
    # stud slot, open at the tip, round end at the stud; wider where the rivet domes pass
    y_stud = -(STUD_POS - p_root)                  # nut recess centre: the stud's position
    y_end = y_stud + SLOT_OVERRUN                   # slot end centre, 1 mm towards the plate
    sw = max(STUD_D, COLLAR_D) + STUD_SLOT_EXTRA
    slot = cad.box2d(-sw / 2, -TAB_L + BRIDGE_L, sw / 2, y_end).union(cad.circle2d(sw, x=0.0, y=y_end))
    dw = DOME_D + DOME_SLOT_EXTRA
    y_dome_top = -(DOME1_POS - DOME_D / 2 - DOME_SLOT_EXTRA / 2 - SLOT_OVERRUN - p_root)
    dome = cad.box2d(-dw / 2, -TAB_L + BRIDGE_L, dw / 2, y_dome_top)
    return tab, slot.union(dome), y_stud


def _rail_xs():
    edge = PLATE_W / 2
    return [edge - RAIL_EDGE0, edge - RAIL_EDGE0 - RAIL_PITCH]    # positive-side rail centres


def _dovetail(x, y_top, length, neck, head, h, z0):
    """Dovetail bar along Y (narrow at z0, wide at z0 + h), centred on x, ending at y_top and running down."""
    prof = cad.Polygon([(x - neck / 2, 0.0), (x + neck / 2, 0.0), (x + head / 2, h), (x - head / 2, h)])
    bar = cad.rotate(cad.extrude(prof, length), x=90.0)        # profile (x, h) -> (x, z); length -> -y
    return cad.translate(bar, y=y_top, z=z0)


def _hex(x, y):
    r = MESH_AF / math.sqrt(3.0)              # circumradius; flats at +-AF/2 in X
    pts = [(x + r * math.cos(math.radians(30 + 60 * k)), y + r * math.sin(math.radians(30 + 60 * k))) for k in range(6)]
    return cad.Polygon(pts)


def _mesh_centres(x0, x1):
    """Hex centres filling the box x0..x1 (mesh region, border already removed), y from the lip border to the top border."""
    pitch = MESH_AF + MESH_RIB
    rowp = pitch * math.sqrt(3.0) / 2
    r = MESH_AF / math.sqrt(3.0)
    y_lo = LIP_T + MESH_BORDER + r
    y_hi = PLATE_H - MESH_BORDER - r
    n = int((y_hi - y_lo) // rowp) + 1
    y_start = y_lo + ((y_hi - y_lo) - (n - 1) * rowp) / 2
    cols = int((x1 - x0 - MESH_AF) // pitch) + 1
    x_start = x0 + ((x1 - x0) - ((cols - 1) * pitch + MESH_AF)) / 2 + MESH_AF / 2
    pts = []
    for k in range(n):
        x = x_start + (pitch / 2 if k % 2 else 0.0)
        while x <= x1 - MESH_AF / 2 + 1e-6:
            pts.append((x, y_start + k * rowp))
            x += pitch
    return pts


def _centre_mesh():
    half = PLATE_W / 2 - OVERLAP - MESH_BORDER      # keeps the rail-groove zone (overlap) and a border solid
    r = MESH_AF / math.sqrt(3.0)
    kx = TONGUE_W / 2 + MESH_BORDER                 # and the zone where the V's tongue, keys and bolts sit
    ky = TONGUE_L + MESH_BORDER
    return [(x, y) for x, y in _mesh_centres(-half, half)
            if not (abs(x) - MESH_AF / 2 < kx and y - r < ky)]


def _extender_mesh():
    return _mesh_centres(PLATE_W / 2 + MESH_BORDER, PLATE_W / 2 + EXT_VIS_W - MESH_BORDER)


def _hexagon(af, x=0.0, y=0.0):
    rr = af / math.sqrt(3.0)
    return cad.Polygon([(x + rr * math.cos(math.radians(60 * k)), y + rr * math.sin(math.radians(60 * k))) for k in range(6)])


def _key_span():
    return KEY_END, TONGUE_L - KEY_END          # y range of the keys on the tongue (V frame = plate frame)


def _centre():
    plate = _top_rounded(0.0, PLATE_W, PLATE_H).intersection(cad.box2d(-PLATE_W / 2, 0.0, PLATE_W / 2, PLATE_H))
    outline = plate
    for x, y in _centre_mesh():
        outline = outline.difference(_hex(x, y))
    body = cad.chamfered_extrude(outline, PLATE_T, bottom=FOOT_CHAMFER)
    lip = cad.translate(cad.box(PLATE_W, LIP_T, LIP_H + 0.05, center_xy=False), x=-PLATE_W / 2, z=PLATE_T - 0.05)
    body = cad.union(body, lip)
    cutters = []
    for sx in (-1, 1):
        for x in _rail_xs():
            # extender rail grooves: open at the top edge, closed at the bottom end (y = RAIL_Y0)
            cutters.append(_dovetail(sx * x, PLATE_H + 1.0, PLATE_H + 1.0 - RAIL_Y0,
                                     RAIL_NECK + 2 * RAIL_CLEAR, RAIL_HEAD + 2 * RAIL_CLEAR,
                                     RAIL_H + RAIL_CLEAR + 0.05, -0.05))
        # V key grooves: open at the bottom edge, closed where the key ends (the V's top end seats there)
        k0, k1 = _key_span()
        cutters.append(_dovetail(sx * KEY_X, k1, k1 + 1.0, RAIL_NECK + 2 * RAIL_CLEAR, RAIL_HEAD + 2 * RAIL_CLEAR,
                                 RAIL_H + RAIL_CLEAR + 0.05, -0.05))
    for by in (BOLT_Y1, BOLT_Y2):
        hole = THREAD_D + 2 * BOLT_HOLE_CLEAR
        cutters.append(cad.translate(cad.cylinder(hole, PLATE_T + 2.0), y=by, z=-1.0))
        head = BOLT_HEAD_D + 2 * BOLT_HOLE_CLEAR      # 90 deg countersink on the music face
        depth = (head - hole) / 2
        cs = cad.cylinder(hole, depth + 0.01, d_top=head)
        cutters.append(cad.translate(cs, y=by, z=PLATE_T - depth))
        cutters.append(cad.translate(cad.cylinder(head, 2.0), y=by, z=PLATE_T))
    return cad.difference(body, *cutters)


def _v_tab():
    """The V (rev 12 separate part): the tested V below y = 0, a tongue above it that sits behind the
    centre plate, 2 dovetail keys on the tongue front, 2 bolt holes with nut pockets in the back."""
    tab, slots, y_stud = _tab_outline()
    tongue = _top_rounded(0.0, TONGUE_W, TONGUE_L).intersection(cad.box2d(-TONGUE_W / 2, -0.5, TONGUE_W / 2, TONGUE_L))
    outline = tab.difference(slots).union(tongue)
    body = cad.chamfered_extrude(outline, TAB_T, bottom=FOOT_CHAMFER)
    boss2d = tab.intersection(cad.box2d(-TIP_BOSS_W / 2, -TAB_L, TIP_BOSS_W / 2, -TAB_L + TIP_BOSS_L)).difference(slots)
    body = cad.union(body, cad.extrude(boss2d, TIP_BOSS_T - TAB_T + 0.05, z0=TAB_T - 0.05))
    k0, k1 = _key_span()
    for sx in (-1, 1):
        body = cad.union(body, _dovetail(sx * KEY_X, k1, k1 - k0, RAIL_NECK, RAIL_HEAD, RAIL_H + 0.05, TAB_T - 0.05))
    # gable relief profile (x, z): no flat roof, so it prints as two sloped faces without support
    prof = cad.Polygon([(-RELIEF_W / 2, -1.0), (RELIEF_W / 2, -1.0), (RELIEF_W / 2, 0.0), (0.0, BRIDGE_RELIEF), (-RELIEF_W / 2, 0.0)])
    relief = cad.translate(cad.rotate(cad.extrude(prof, BRIDGE_L + 2.0), x=90.0), y=-TAB_L + BRIDGE_L + 1.0)
    w = 60.0
    tri = cad.Polygon([(-TAB_L + TAB_LEADIN + 0.1, -0.1), (-TAB_L - 1.0, TAB_LEADIN + 1.0), (-TAB_L - 1.0, -0.1)])
    wedge = cad.rotate(cad.rotate(cad.extrude(tri, w), x=90.0), z=90.0)   # (u, v, l) -> (l, u, v): u = y, v = z
    wedge = cad.translate(wedge, x=-w / 2)
    recess = cad.extrude(cad.circle2d(NUT_RECESS_D, x=0.0, y=y_stud), NUT_RECESS_DEPTH + 1.0, z0=TAB_T - NUT_RECESS_DEPTH)
    cutters = [relief, wedge, recess]
    for by in (BOLT_Y1, BOLT_Y2):
        cutters.append(cad.translate(cad.cylinder(THREAD_D + 2 * BOLT_HOLE_CLEAR, TAB_T + 2.0), y=by, z=-1.0))
        cutters.append(cad.extrude(_hexagon(JAM_AF + 2 * JAM_CLEAR, 0.0, by), JAM_POCKET + 1.0, z0=-1.0))
    return cad.translate(cad.difference(body, *cutters), y=TAB_SHIFT_Y)


def _bolt(x, y):
    """Printed M6 countersunk bolt, printed head down (flat head face on the bed)."""
    head_h = (BOLT_HEAD_D - THREAD_D) / 2
    head = cad.cylinder(BOLT_HEAD_D, head_h, d_top=THREAD_D)
    shank = cad.translate(_thread_bolt(THREAD_D, THREAD_P, BOLT_L - head_h + 0.05, -BOLT_CLEAR), z=head_h - 0.05)
    tip = cad.union(cad.cylinder(THREAD_D + 2.0, BOLT_L - 0.8),
                    cad.translate(cad.cylinder(THREAD_D + 2.0, 1.6, d_top=THREAD_D - 2.0), z=BOLT_L - 0.8))
    bolt = cad.union(head, cad.intersection(shank, tip))
    socket = cad.extrude(_hexagon(BOLT_HEX + 0.2), 2.6, z0=-1.0)    # 4 mm hex key, 1.6 deep (layer boundary)
    return cad.translate(cad.difference(bolt, socket), x=x, y=y)


def _jam_nut(x, y):
    body = cad.extrude(_hexagon(JAM_AF), JAM_T)
    thread = cad.translate(_thread_bolt(THREAD_D, THREAD_P, JAM_T + 2.0, THREAD_CLEAR), z=-1.0)
    lead = THREAD_D / 2 + THREAD_CLEAR + 0.5
    cone_b = cad.translate(cad.cylinder(2 * lead + 1.0, lead, d_top=0.1), z=-0.5)
    cone_t = cad.translate(cad.mirror(cad.cylinder(2 * lead + 1.0, lead, d_top=0.1), "z"), z=JAM_T + 0.5)
    return cad.translate(cad.difference(body, thread, cone_b, cone_t), x=x, y=y)


def _extender_right():
    x_in = PLATE_W / 2 - OVERLAP                   # inner end of the strip
    x_out = PLATE_W / 2 + EXT_VIS_W                # outer edge
    x_step = PLATE_W / 2 + REBATE_CLEAR            # rebate wall (the centre plate edge sits against it)
    outline = _top_rounded((x_in + x_out) / 2, x_out - x_in, EXT_H).intersection(cad.box2d(x_in, 0.0, x_out, EXT_H))
    for x, y in _extender_mesh():
        outline = outline.difference(_hex(x, y))
    body = cad.chamfered_extrude(outline, EXT_T, bottom=FOOT_CHAMFER)
    rebate = cad.translate(cad.box(x_step - x_in + 1.0, EXT_H + 2.0, REBATE_D + 1.0, center_xy=False),
                           x=x_in - 1.0, y=-1.0, z=EXT_T - REBATE_D)
    body = cad.difference(body, rebate)
    lip = cad.translate(cad.box(x_out - x_step, LIP_T, LIP_H + 0.05, center_xy=False), x=x_step, z=EXT_T - 0.05)
    rails = []
    for x in _rail_xs():
        rails.append(_dovetail(x, EXT_H - RAIL_TOP_GAP, EXT_H - RAIL_TOP_GAP - RAIL_Y0, RAIL_NECK, RAIL_HEAD,
                               RAIL_H + 0.05, EXT_T - REBATE_D - 0.05))
    return cad.union(body, lip, *rails)


def _thread_bolt(d_major, pitch, length, clear):
    """Right-hand metric thread envelope (contains the ISO bolt profile) grown by `clear` radially; z from 0 to length."""
    h = 0.8660254 * pitch
    r_maj = d_major / 2 + clear
    r_min = d_major / 2 - 5 * h / 8 + clear
    n = 72
    pts = []
    for i in range(n):
        u = i / n                                  # fraction of a turn = fraction of the pitch
        a = min(u, 1 - u)                          # distance from the crest along the axis, in pitches
        if a <= 1 / 16:
            r = r_maj                              # crest flat (P/8)
        else:
            # flank runs to the middle of the pitch (no flat at the nut's minor diameter): about 51 deg
            # from vertical instead of ISO 60, so the nut prints without support; it still contains the
            # ISO bolt profile, so it only adds flank clearance
            r = r_maj - (a - 1 / 16) / (1 / 2 - 1 / 16) * (r_maj - r_min)
        t = 2 * math.pi * u
        pts.append((r * math.cos(t), r * math.sin(t)))
    cs = cad.cross_section(cad.Polygon(pts))
    turns = length / pitch
    return cad.m3.Manifold.extrude(cs, length, int(round(turns * n)), 360.0 * turns)   # one division per profile vertex: exact helical facets


def _nut():
    body = cad.cylinder(NUT_OD, NUT_H)
    notches = [cad.translate(cad.cylinder(NUT_GRIP_D, NUT_H + 2.0), x=NUT_OD / 2 * math.cos(2 * math.pi * k / NUT_GRIP_N),
                             y=NUT_OD / 2 * math.sin(2 * math.pi * k / NUT_GRIP_N), z=-1.0) for k in range(NUT_GRIP_N)]
    thread = cad.translate(_thread_bolt(THREAD_D, THREAD_P, NUT_H + 2.0, THREAD_CLEAR), z=-1.0)
    lead = THREAD_D / 2 + THREAD_CLEAR + 0.5
    cone_b = cad.translate(cad.cylinder(2 * lead + 1.0, lead, d_top=0.1), z=-0.5)          # 45 deg entry, bed side
    cone_t = cad.translate(cad.mirror(cad.cylinder(2 * lead + 1.0, lead, d_top=0.1), "z"), z=NUT_H + 0.5)
    nut = cad.difference(body, thread, cone_b, cone_t, *notches)
    return cad.translate(nut, x=NUT_POS[0], y=NUT_POS[1])


def build_part():
    """Return {suffix: Solid}: centre plate, 2 extenders, the V, 2 bolts, 2 nuts and the stud's thumb nut."""
    right = _extender_right()          # built in its assembled x position (overlap strip under the centre plate)
    left = cad.mirror(right, "x")
    parts = {"centre": _centre(),
             "extender-right": cad.translate(right, x=LAYOUT_SHIFT),
             "extender-left": cad.translate(left, x=-LAYOUT_SHIFT),
             "v-tab": _v_tab(),
             "nut": _nut()}
    for name, (x, y) in SMALL_POS.items():
        parts[name] = _bolt(x, y) if name.startswith("bolt") else _jam_nut(x, y)
    return parts
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
