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
import assembly  # noqa: E402
import cad  # noqa: E402
import printcheck  # noqa: E402
import printers  # noqa: E402
from safeio import safe_text  # noqa: E402

PROJECT_DIR = Path(__file__).resolve().parent
FITS = cad.load_fits(PROJECT_DIR)  # per-side clearances: fits.json if present, else defaults

# ===================== PARAMETERS START (edit only this block) =====================
NAME = "hair-band"          # output file stem: a-z, 0-9 and dashes only
MATERIAL = "PETG"                # print.material (primary); finalize rebuilds with PLA too
COLOR = "#2b2b2b"                # preview colour: black like the original
COLOUR_NAME = "black"            # filament colour in words; goes to the print hand-off

PRINTER = "generic"              # printer profile (scripts/printers.py)
PRINTER_BED = (180, 180, 180)    # user: 180 mm bed (A1 mini class)
NOZZLE = 0.4                     # user: 0.4 nozzle; minimum wall = 2 x NOZZLE
LAYER = 0.2                      # band height 8 = 40 layers
OVERHANG_LIMIT = 45              # degrees from vertical this printer manages without support
SUPPORTS_ALLOWED = False         # flat print, no supports (teeth keeled, openings bridged)
EXPECTED_BODIES = 1              # one solid; a second body means a loose piece
ASSEMBLY = False

# --- outline (spec F1) ---
INNER_W = 116.0                  # D1 inside width at the widest point (estimated, photo 131012)
OUTER_L = 147.0                  # D2 crown outer face to the tips, Y (estimated, photo 131012)
BAND_H = 8.0                     # D3 band height lying flat = link height (estimated, photo 131024)
TIP_GAP = 25.0                   # D4 gap between the tips, inner faces (estimated, photo 131012)
WIDEST_Y = 70.0                  # D5 widest point from the crown outer face (estimated, photo 131012)

# --- curb chain links (spec F2): round oval wire links, slanted and twisted, interlocked ---
LINK_PITCH = 9.0                 # D7 nominal link pitch; adjusted so whole links end at the tips
LINK_L = 14.0                    # D8 link outer length along its own long axis
WIRE_D = 2.4                     # D27 link wire diameter (photo 131024: rails ~2.5)
LINK_SLANT = 15.0                # D28 link tilt in the face, deg (the slanted ovals of photo 131024)
LINK_YAW = 10.0                  # D29 link twist about Z, deg: each link's leading end passes in front of
                                 #     the next link, its trailing end behind (the curb / braid look)
KEEL_DEG = 50.0                  # D30 hidden keel under every wire and tooth, slope from horizontal:
                                 #     40 deg from vertical, so the round wire prints without support
BED_SINK = 0.4                   # D31 the lowest wire is cut flat this much for bed contact (2 layers)
LINK_SEGMENTS = 40               # hull segments per link (smoothness)
WIRE_FACETS = 20                 # facets round the wire

# --- grip teeth (spec F3) ---
TOOTH_D = 1.4                    # D13 tooth diameter (user)
TOOTH_L = 2.5                    # D14 tooth length from the innermost body face
TOOTH_GAP = 3.0                  # D15 spacing of the 2 teeth per link per row
TOOTH_Z_LOW = 1.0                # D16 lower row axis Z (keel touches the bed)
TOOTH_Z_HIGH = 6.7               # D17 upper row axis Z
TEETH_SPAN = 170.0               # D18 toothed centreline length, centred on the crown

# --- rev 4: stiffness, support-free teeth, smooth tips ---
SPINE_T = 2.6                    # D32 hidden spine, radial thickness from the inner face: stiffens the band and
                                 #     carries every upper wire and tooth, so nothing starts in mid-air
SPINE_H = 7.6                    # D33 spine height (round top), just under the 8 mm wire crowns
TIP_PAD_L = 10.0                 # D34 rounded end pad at each tip, length along the band
GAP_MARGIN = 0.3                 # D35 see-through windows in the spine on the toothless arms: clearance from
                                 #     every wire edge
BRIDGE_MAX = 1.6                 # D36 longest flat (bridged) window top; beyond it the top slopes down at D30.
                                 #     Under the spine depth x 2/3, so printcheck sees a bridge held at both ends

PROBES_INSIDE = [
    (-0.69, 2.32, 6.4),          # crown link, top of its wire
    (1.5, 6.4, TOOTH_Z_HIGH),    # crown upper tooth, 2 mm in from the band
    (0.0, 3.8, 3.8),             # spine at the crown, behind the crown link opening
]
PROBES_OUTSIDE = [
    (0.0, 1.0, 3.8),             # crown link opening: open in the outer half (pocket in front of the spine)
    (0.0, WIDEST_Y, BAND_H / 2), # middle of the C
    (0.0, OUTER_L - 2.0, BAND_H / 2),  # between the tips
]
# ====================== PARAMETERS END ======================


# ===================== GEOMETRY START =====================
import math  # noqa: E402

import manifold3d as m3  # noqa: E402
import numpy as np  # noqa: E402

# Chain frame: u = arc length along the band centreline (0 at the crown), w = radial
# (+ outward, away from the head), z = up. Every wire is swept as hulls of "drops" (a
# sphere with a cone under it, KEEL_DEG steep) whose centres are mapped onto the curve.
# A drop is round about Z, so mapping its centre keeps the keel exact on the curve: the
# round wire shows on top and outside, the keel underneath faces the bed, no supports.


def _drop_points(r):
    """Vertices of a drop: sphere of radius r over a cone whose sides slope KEEL_DEG."""
    sphere = m3.Manifold.sphere(r, WIRE_FACETS)
    pts = np.asarray(sphere.to_mesh().vert_properties, dtype=float)[:, :3]
    apex = r / math.cos(math.radians(KEEL_DEG))              # cone tangent to the sphere
    return np.vstack([pts, [[0.0, 0.0, -apex]]])


def _centreline():
    """Right half of the centreline from the crown (s = 0) to the tip: s, points, tangents, s_end."""
    r_end = _body_t() / 2
    a = INNER_W / 2 + r_end
    b_top = WIDEST_Y - r_end
    x_tip = TIP_GAP / 2 + r_end
    y_end = OUTER_L - r_end                                   # the end link reaches OUTER_L
    t_end = math.acos(x_tip / a)
    b_bot = (y_end - WIDEST_Y) / math.sin(t_end)
    phi = np.linspace(0.0, math.pi / 2, 3000)
    upper = np.c_[a * np.sin(phi), WIDEST_Y - b_top * np.cos(phi)]
    t = np.linspace(0.0, t_end, 3000)[1:]
    lower = np.c_[a * np.cos(t), WIDEST_Y + b_bot * np.sin(t)]
    pts = np.vstack([upper, lower])
    s = np.r_[0.0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    tan = np.gradient(pts, s, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    s_end = float(s[-1])
    d = np.linspace(0.0, 20.0, 40)[1:]                        # straight run-out past the tip
    pts = np.vstack([pts, pts[-1] + d[:, None] * tan[-1]])
    tan = np.vstack([tan, np.repeat(tan[-1:], len(d), axis=0)])
    s = np.r_[s, s_end + d]
    return s, pts, tan, s_end


def _to_world(uwz, s, pts, tan):
    """(u, w, z) chain coordinates -> world XYZ on the curved band."""
    u, w, z = uwz[:, 0], uwz[:, 1], uwz[:, 2]
    a = np.abs(u)
    sign = np.where(u < 0, -1.0, 1.0)
    x = np.interp(a, s, pts[:, 0]) * sign
    y = np.interp(a, s, pts[:, 1])
    tx = np.interp(a, s, tan[:, 0])
    ty = np.interp(a, s, tan[:, 1]) * sign
    n = np.hypot(tx, ty)
    nx, ny = -ty / n, tx / n                                  # inward normal
    return np.c_[x - w * nx, y - w * ny, z]


def _link_shape():
    """Wire centreline half-axes (A along the link, B across) and the link's centre height."""
    r = WIRE_D / 2
    th = math.radians(LINK_SLANT)
    a = LINK_L / 2 - r                                        # D8 is the outer length
    zc = (BAND_H - BED_SINK) / 2                              # wire spans -BED_SINK .. BAND_H, cut at 0
    hz = (BAND_H + BED_SINK) / 2 - r                          # half the Z travel of the wire centre
    b = math.sqrt(hz ** 2 - (a * math.sin(th)) ** 2) / math.cos(th)
    return a, b, zc


def _body_t():
    """D6: radial thickness of the chain = wire + the twist's in/out travel."""
    a, b, _ = _link_shape()
    th, ps = math.radians(LINK_SLANT), math.radians(LINK_YAW)
    reach_u = math.sqrt((a * math.cos(th)) ** 2 + (b * math.sin(th)) ** 2)
    return WIRE_D + 2 * reach_u * math.sin(ps)


def _link_path(uc):
    """Closed wire centreline of one link, chain coordinates, LINK_SEGMENTS points."""
    a, b, zc = _link_shape()
    th, ps = math.radians(LINK_SLANT), math.radians(LINK_YAW)
    t = np.linspace(0.0, 2 * math.pi, LINK_SEGMENTS, endpoint=False)
    x, z = a * np.cos(t), b * np.sin(t)
    u1 = x * math.cos(th) - z * math.sin(th)                  # slant in the face
    z1 = x * math.sin(th) + z * math.cos(th)
    return np.c_[uc + u1 * math.cos(ps), u1 * math.sin(ps), zc + z1]   # twist about Z


def _sweep(points_world, drop, closed):
    """Hulls of drops at consecutive points."""
    n = len(points_world)
    segs = []
    for i in range(n if closed else n - 1):
        p, q = points_world[i], points_world[(i + 1) % n]
        segs.append(m3.Manifold.hull_points(np.vstack([drop + p, drop + q])))
    return segs


def _window_poly(pitch):
    """D35: the largest support-free window behind one link, in (u - link centre, z).

    The wires of the link and its two neighbours, keels included, are projected along the band
    normal; what stays clear (shrunk by GAP_MARGIN) is where the band could be see-through. The
    window is the part of that clear area under a roof that is flat (a bridge, at most BRIDGE_MAX
    long, anchored on both sides) and slopes down at KEEL_DEG beyond that: each column runs from the
    material below up to the roof, so the spine above never overhangs on one side only.
    """
    from shapely.geometry import LineString, Point, Polygon, box
    from shapely.ops import unary_union
    r = WIRE_D / 2
    apex = r / math.cos(math.radians(KEEL_DEG))
    ring = [(r * math.cos(t), r * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 24, endpoint=False)]
    sil = []
    for k in (-1, 0, 1):
        path = _link_path(k * pitch)
        for i in range(len(path)):
            p, q = path[i], path[(i + 1) % len(path)]
            cloud = [(c[0] + du, c[2] + dz) for c in (p, q) for du, dz in ring + [(0.0, -apex)]]
            sil.append(Polygon(cloud).convex_hull)
    clear = box(-pitch, 0.0, pitch, BAND_H).difference(unary_union(sil)).buffer(-GAP_MARGIN)
    parts_ = [g for g in getattr(clear, "geoms", [clear]) if g.area > 0.5]
    if not parts_:
        return None
    _, zc = _link_shape()[1:]
    clear = min(parts_, key=lambda g: g.distance(Point(0.0, zc)))
    du = 0.05
    cols = []                                                 # per column: free intervals in z
    for u in np.arange(clear.bounds[0], clear.bounds[2] + du, du):
        cut = clear.intersection(LineString([(u, -1.0), (u, BAND_H + 1.0)]))
        segs = [g for g in getattr(cut, "geoms", [cut]) if g.geom_type == "LineString" and not g.is_empty]
        cols.append((u, sorted((min(c[1] for c in g.coords), max(c[1] for c in g.coords)) for g in segs)))
    tk = math.tan(math.radians(KEEL_DEG))
    us_c = np.array([u for u, _ in cols])
    nk = max(len(ivs) for _, ivs in cols)
    lo = np.full((nk, len(cols)), np.nan)
    hi = np.full((nk, len(cols)), np.nan)
    for j, (_, ivs) in enumerate(cols):
        for k, (a, b) in enumerate(ivs):
            lo[k, j], hi[k, j] = a, b

    best, best_a = None, 0.0
    for ua in np.arange(clear.bounds[0], clear.bounds[2], 0.1):
        z0 = math.ceil(clear.bounds[1] / LAYER) * LAYER
        for zb in np.arange(z0, clear.bounds[3] + 1e-9, LAYER):   # flat top on a layer line
            for half in np.arange(0.0, BRIDGE_MAX / 2 + 1e-9, 0.25):
                # roof: flat (a bridge) over 2 * half, then down at KEEL_DEG on both ends
                roof = zb - tk * np.maximum(np.abs(us_c - ua) - half, 0.0)
                inside = (lo < roof) & (roof <= hi)
                cols_in = np.flatnonzero(inside.any(axis=0))
                if len(cols_in) < 3 or np.any(np.diff(cols_in) != 1):
                    continue
                k = inside.argmax(axis=0)
                floor = lo[k[cols_in], cols_in]                  # the smooth top of the material below
                a = (roof[cols_in] - floor).sum() * du
                if a > best_a:
                    best = list(zip(us_c[cols_in], floor, roof[cols_in]))
                    best_a = a
    if best is None:
        return None
    return [(u, z) for u, z, _ in best] + [(u, z) for u, _, z in reversed(best)]


def _window_cutter(poly, uc, w0, w1, s, pts, tan):
    """Prism of the window polygon, (u, z) shifted to uc, from w0 to w1, bent onto the band."""
    cs = m3.CrossSection([np.asarray(poly, dtype=float)])
    solid = m3.Manifold.extrude(cs, w1 - w0, n_divisions=1)   # local x = u, y = z, z = w
    mesh = solid.to_mesh()
    v = np.asarray(mesh.vert_properties, dtype=float)[:, :3]
    uwz = np.c_[uc + v[:, 0], w0 + v[:, 2], v[:, 1]]
    v_world = _to_world(uwz, s, pts, tan)
    out = m3.Manifold(m3.Mesh(vert_properties=v_world.astype(np.float32),
                              tri_verts=np.asarray(mesh.tri_verts, dtype=np.uint32)))
    if out.volume() < 0:
        out = m3.Manifold(m3.Mesh(vert_properties=v_world.astype(np.float32),
                                  tri_verts=np.asarray(mesh.tri_verts, dtype=np.uint32)[:, ::-1].copy()))
    return out


def build_part():
    s, pts, tan, s_end = _centreline()
    a, b, zc = _link_shape()
    th = math.radians(LINK_SLANT)
    reach_u = math.sqrt((a * math.cos(th)) ** 2 + (b * math.sin(th)) ** 2) * math.cos(math.radians(LINK_YAW))
    reach = s_end + _body_t() / 2 - reach_u - WIRE_D / 2       # last link's far end at the tip
    n_half = max(1, round(reach / LINK_PITCH))
    pitch = reach / n_half                                    # D7 adjusted to whole links
    wire = _drop_points(WIRE_D / 2)
    parts, paths = [], []
    for i in range(-n_half, n_half + 1):
        path = _link_path(i * pitch)
        paths.append(path)
        parts += _sweep(_to_world(path, s, pts, tan), wire, closed=True)

    # D32/D33 hidden spine: a round-topped wall on the inner side of the chain, tip to tip.
    # Its inner face is flush with the chain's inner face; the bottom keel is cut by the bed.
    w_in = -_body_t() / 2                                     # chain inner face
    rs = SPINE_T / 2
    spine_drop = _drop_points(rs)
    rp = _body_t() / 2                                        # tip pad radius (D34 below)
    blend = 3.0                                               # spine -> tip pad blend length
    u_sp = s_end - TIP_PAD_L - blend                          # the spine runs to here, then blends
    n_sp = max(2, int(math.ceil(2 * u_sp / 2.0)))             # one hull every ~2 mm
    spine_c = lambda u: np.array([[u, w_in + rs, rs], [u, w_in + rs, SPINE_H - rs]])
    us = np.linspace(-u_sp, u_sp, n_sp)
    spine = []
    for u0, u1 in zip(us[:-1], us[1:]):
        cw = _to_world(np.vstack([spine_c(u0), spine_c(u1)]), s, pts, tan)
        spine.append(m3.Manifold.hull_points(np.vstack([spine_drop + p for p in cw])))
    spine = m3.Manifold.batch_boolean(spine, m3.OpType.Add)

    # D35 see-through windows: on every link whose window clears the toothed zone and the tip
    # blend, cut the spine behind the link's clear opening (window shape from _window_poly).
    win = _window_poly(pitch)
    windows = []
    if win is not None:
        wu = np.asarray(win)[:, 0]
        for i in range(-n_half, n_half + 1):
            lo, hi = sorted((i * pitch + wu.min(), i * pitch + wu.max()), key=abs)
            if abs(lo) < TEETH_SPAN / 2 + TOOTH_D or abs(hi) > u_sp - 1.0 or lo * hi < 0:
                continue
            windows.append(_window_cutter(win, i * pitch, w_in - 0.5, w_in + SPINE_T + 0.5, s, pts, tan))
    if windows:
        spine = spine - m3.Manifold.batch_boolean(windows, m3.OpType.Add)
    parts.append(spine)
    print(f"spine windows: {len(windows)}" + (f", each {np.ptp(wu):.1f} long x "
          f"{np.ptp(np.asarray(win)[:, 1]):.1f} high" if win is not None else ""))
    pad_drop = _drop_points(rp)
    for sgn in (-1.0, 1.0):                                   # blend: spine section hulled with the pad section
        sp_w = _to_world(spine_c(sgn * u_sp), s, pts, tan)
        pd_w = _to_world(np.array([[sgn * (u_sp + blend), 0.0, rp], [sgn * (u_sp + blend), 0.0, BAND_H - rp]]),
                         s, pts, tan)
        parts.append(m3.Manifold.hull_points(np.vstack([spine_drop + p for p in sp_w] + [pad_drop + p for p in pd_w])))

    # D34 tip pads: a smooth capsule over the last link, as thick as the chain, round at the end.
    # Links and spine are trimmed inside the pad (all but its first 2 mm), so no wire end or
    # spine corner pokes through the pad's rounded surface.
    pads, trims = [], []
    big = 4.0 * BAND_H                                        # trim block height, well past the band
    w_trim = _body_t() + 1.0                                  # trim block half-width: the band, not the other tip
    for sgn in (-1.0, 1.0):
        us = np.linspace(s_end - TIP_PAD_L, s_end, 6)
        for u0, u1 in zip(us[:-1], us[1:]):
            c = np.array([[sgn * u0, 0.0, rp], [sgn * u0, 0.0, BAND_H - rp],
                          [sgn * u1, 0.0, rp], [sgn * u1, 0.0, BAND_H - rp]])
            cw = _to_world(c, s, pts, tan)
            pads.append(m3.Manifold.hull_points(np.vstack([pad_drop + p for p in cw])))
        ut = np.linspace(s_end - TIP_PAD_L + 2.0, s_end + 19.0, 8)
        for u0, u1 in zip(ut[:-1], ut[1:]):
            c = np.array([[sgn * u, w, z] for u in (u0, u1) for w in (-w_trim, w_trim) for z in (-big, big)])
            trims.append(m3.Manifold.hull_points(_to_world(c, s, pts, tan)))

    # F3 grip teeth: drop-section pins from the spine straight inward. Under each tooth a web
    # whose lower edge climbs from the spine face to the tooth tip at KEEL_DEG, so every tooth
    # grows out of the spine layer by layer instead of starting in mid-air.
    tooth = _drop_points(TOOTH_D / 2)
    r_t = TOOTH_D / 2
    w_tip = w_in - TOOTH_L + r_t                              # round tip ends D14 beyond the inner face
    w_low = w_in + r_t                                        # web foot, just inside the spine face
    drop_z = (w_low - w_tip) * math.tan(math.radians(KEEL_DEG))
    n_teeth = 0
    for i in range(-n_half, n_half + 1):
        for du in (-TOOTH_GAP / 2, TOOTH_GAP / 2):
            for u_t, z_t in ((i * pitch + du, TOOTH_Z_HIGH), (i * pitch + pitch / 2 + du, TOOTH_Z_LOW)):
                if abs(u_t) > TEETH_SPAN / 2:
                    continue
                c = np.array([[u_t, w_in + rs, min(z_t, SPINE_H - rs)],   # root, in the spine
                              [u_t, w_tip, z_t],                          # tip
                              [u_t, w_low, z_t - drop_z]])                # web foot
                cw = _to_world(c, s, pts, tan)
                pads.append(m3.Manifold.hull_points(np.vstack([tooth + p for p in cw])))
                n_teeth += 1

    chain = m3.Manifold.batch_boolean(parts, m3.OpType.Add)                 # links + spine
    chain = chain - m3.Manifold.batch_boolean(trims, m3.OpType.Add)        # cleared inside the tip pads
    chain = m3.Manifold.batch_boolean([chain] + pads, m3.OpType.Add)       # + tip pads + teeth
    lo = chain.bounding_box()
    bed = m3.Manifold.cube((400.0, 400.0, BAND_H + 5.0)).translate((-200.0, -200.0, 0.0))
    chain = cad.intersection(chain, bed)                      # cut the keels and the lowest wire flat at z = 0
    print(f"links: {2 * n_half + 1} at pitch {pitch:.3f}; link A {a:.2f} B {b:.2f}; "
          f"body {_body_t():.2f}; teeth: {n_teeth}; z before cut {lo[2]:.2f}")
    return chain
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
        profile = printers.get(g.get("PRINTER"))
    except ValueError as exc:
        print(f"refusing: {safe_text(exc)}", file=sys.stderr)
        return 2

    parts = build_part()
    if not isinstance(parts, dict):
        parts = {"": parts}
    together = bool(g.get("ASSEMBLY", False)) and len(parts) > 1
    colours = {sfx: str(_per_part(g.get("COLOUR_NAME"), sfx) or "") for sfx in parts}
    n_colours = len(set(colours.values())) if len(parts) > 1 else 1
    try:
        bed = printers.bed_for(profile, n_colours, g.get("PRINTER_BED"))
    except ValueError as exc:
        print(f"refusing: {safe_text(exc)}", file=sys.stderr)
        return 2
    results = []
    for suffix, solid in parts.items():
        try:
            part_name = name if not suffix else cad.validate_name(f"{name}-{suffix}")
        except ValueError as exc:
            print(f"refusing: {safe_text(exc)}", file=sys.stderr)
            return 2
        mesh = cad.to_trimesh(solid)
        res = printcheck.check_printable(
            mesh, bed=bed, layer=g["LAYER"], nozzle=g["NOZZLE"],
            overhang_deg=g["OVERHANG_LIMIT"], supports=g["SUPPORTS_ALLOWED"],
            expected_bodies=_per_part(g["EXPECTED_BODIES"], suffix),
            thin_wall_samples=args.thin_walls,
            probes_inside=_per_part(g.get("PROBES_INSIDE", ()), suffix) or (),
            probes_outside=_per_part(g.get("PROBES_OUTSIDE", ()), suffix) or (),
            standalone=not together,
        )
        print(res.summary(part_name))
        results.append((part_name, suffix, mesh, res))

    joined = None
    if together:
        joined = assembly.check_assembly(
            parts, bed=bed, layer=g["LAYER"], nozzle=g["NOZZLE"], overhang_deg=g["OVERHANG_LIMIT"],
            supports=g["SUPPORTS_ALLOWED"], expected_bodies=g.get("ASSEMBLY_BODIES", 1),
            nozzles=profile["nozzles"])
        print(joined.summary(f"{name} (all {len(parts)} colour parts joined)"))
    two_nozzle_bed = not g.get("PRINTER_BED") and n_colours >= 2 and bool(profile.get("bed_two_nozzles"))
    notes = printers.notes(profile, g["MATERIAL"], n_colours, two_nozzle_bed)
    for note in notes:
        print(f"note ({profile['label']}): {note}")

    failed = [r[0] for r in results if not r[3].ok] + ([name + " (joined)"] if joined and not joined.ok else [])
    if failed:
        print(f"\nprintcheck failed for {', '.join(failed)}: nothing written. "
              "Fix the parameters or the geometry and run again.", file=sys.stderr)
        return 1
    if args.check:
        print("\ncheck only: nothing written")
        return 0
    params = cad.param_snapshot(g)
    params["FITS"] = FITS
    extra = {"printer": profile["name"], "assembly": together, "printer_notes": notes}
    if joined is not None:
        extra["assembly_check"] = joined.to_dict()
    handoff = []
    for part_name, suffix, mesh, res in results:
        hex_colour = _per_part(g.get("COLOR"), suffix)
        try:
            stl, meta = cad.write_part(out_dir, part_name, mesh, res, material=g["MATERIAL"], params=params,
                                       color=hex_colour, bed=bed, extra=dict(extra, colour=colours[suffix]))
        except (ValueError, OSError) as exc:
            print(f"refusing: {safe_text(exc)}", file=sys.stderr)
            return 2
        print(f"wrote {stl.relative_to(PROJECT_DIR)} and {meta.relative_to(PROJECT_DIR)}")
        z0, z1 = float(mesh.bounds[0][2]), float(mesh.bounds[1][2])
        handoff.append({"stl": stl.name, "colour": colours[suffix], "colour_hex": hex_colour, "z": (z0, z1),
                        "layers": int(round((z1 - z0) / g["LAYER"])), "volume_mm3": float(mesh.volume)})
    if profile.get("handoff"):
        job = printers.x2d_job(name, handoff, assembly=together, material=g["MATERIAL"], layer=g["LAYER"],
                               nozzle=g["NOZZLE"], supports=g["SUPPORTS_ALLOWED"], profile=profile,
                               printer_notes=notes)
        try:
            path = printers.write_handoff(out_dir, job, profile["handoff_file"])
        except (ValueError, OSError) as exc:
            print(f"refusing: {safe_text(exc)}", file=sys.stderr)
            return 2
        print(f"wrote {path.relative_to(PROJECT_DIR)}: draft job for the {profile['handoff']} skill "
              "(template and filament numbers are filled there)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
