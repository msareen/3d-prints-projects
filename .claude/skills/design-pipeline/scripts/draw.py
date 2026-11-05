#!/usr/bin/env python3
"""draw.py: orthographic drawings of a design-pipeline model, checked against the spec.

Reads every STL (and its JSON metadata) in <project>/processed/model/ and
<project>/processed/spec.json, then writes to <project>/processed/drawings/:

    front.svg  side.svg  top.svg  plan.svg   one view each
    sheet.svg                                all four on an A3 sheet, third-angle
    drawings.json                            scale, edge counts, checks, errors

Views (model coordinates, mm, Z up; the part's front faces -Y):
    front  front elevation: looking along +Y, X to the right, Z up
    side   right side elevation: looking along -X, Y to the right, Z up
    top    top elevation: looking down, X to the right, Y up
    plan   plan view: horizontal section at drawing.plan_cut_z (default mid
           height), looking down; cut material hatched, edges below the cut
Elevations show hidden edges dashed.

Checks (written to drawings.json, printed, and drawn in red on the sheet):
    * envelope: model bounding box vs spec.envelope (+- envelope.tolerance)
    * dimension annotations from spec.drawing.dimensions:
        - value: distance between the annotation points vs the spec value
        - on-geometry: each annotation point must lie on a model edge in that
          view, so a dimension in the spec that the model does not have shows
          up as an error instead of a nice-looking line
    * diameter annotations: model edges must exist at radius d/2 around the centre

Run with the 3d-print-design venv interpreter (numpy, trimesh, shapely):
    python -P draw.py <project_dir>
Exit code: 0 ok, 1 checks failed (files still written), 2 bad input.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import math
import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
import shapely
import trimesh
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union

# ISO 5455 preferred scales as (paper, model)
SCALES = [(50, 1), (20, 1), (10, 1), (5, 1), (2, 1), (1, 1), (1, 2), (1, 5), (1, 10), (1, 20), (1, 50), (1, 100)]
SHEET_W, SHEET_H = 420.0, 297.0      # A3 landscape, paper mm
BORDER = 10.0
TITLE_H = 44.0                       # title block height
LABEL_H = 9.0                        # room above each view for its name
CELL_GAP = 8.0                       # paper mm between view columns
TEXT = 3.5                           # ISO text height
CREASE_DEG = 25.0                    # edges sharper than this are drawn
ON_GEOMETRY_TOL = 0.25               # mm (model) an annotation point may sit off an edge
DEFAULT_VALUE_TOL = 0.05             # mm when the spec dimension has no tolerance

VIEWS = {
    "front": dict(d=(0, 1, 0), u=(1, 0, 0), v=(0, 0, 1), title="FRONT ELEVATION"),
    "side": dict(d=(-1, 0, 0), u=(0, 1, 0), v=(0, 0, 1), title="RIGHT SIDE ELEVATION"),
    "top": dict(d=(0, 0, -1), u=(1, 0, 0), v=(0, 1, 0), title="TOP ELEVATION"),
    "plan": dict(d=(0, 0, -1), u=(1, 0, 0), v=(0, 1, 0), title="PLAN VIEW"),
}

COL_LINE = "#111"
COL_HIDDEN = "#555"
COL_DIM = "#1a4fb0"
COL_ERR = "#d0021b"


# --------------------------------------------------------------------------
# geometry
# --------------------------------------------------------------------------
def _vec(t) -> np.ndarray:
    return np.asarray(t, dtype=np.float64)


class Occluder:
    """Answers 'is this 3D point hidden behind a triangle?' for one view direction.

    Orthographic, so a point is hidden when its (u, v) lies strictly inside a
    projected triangle that is closer to the viewer at that spot. Triangles
    are binned in a uniform 2D grid so each query tests only its cell.
    """

    def __init__(self, tris3: np.ndarray, d, u, v):
        self.u, self.v, self.w = _vec(u), _vec(v), -_vec(d)
        uv = np.stack([tris3 @ self.u, tris3 @ self.v], axis=-1) if len(tris3) else np.zeros((0, 3, 2))
        z = tris3 @ self.w if len(tris3) else np.zeros((0, 3))
        a, b, c = uv[:, 0], uv[:, 1], uv[:, 2]
        v0, v1 = b - a, c - a
        den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
        keep = np.abs(den) > 1e-10            # edge-on triangles hide nothing
        self.a, self.v0, self.v1, self.den = a[keep], v0[keep], v1[keep], den[keep]
        self.za = z[keep, 0]
        self.dzb = z[keep, 1] - z[keep, 0]
        self.dzc = z[keep, 2] - z[keep, 0]
        uv = uv[keep]
        m = len(uv)
        self.m = m
        if m == 0:
            return
        self.lo = uv.reshape(-1, 2).min(0)
        hi = uv.reshape(-1, 2).max(0)
        self.G = int(np.clip(math.sqrt(m) / 1.5, 4, 160))
        self.cs = np.maximum((hi - self.lo) / self.G, 1e-9)
        tmin = np.floor((uv.min(1) - self.lo) / self.cs).astype(np.int64).clip(0, self.G - 1)
        tmax = np.floor((uv.max(1) - self.lo) / self.cs).astype(np.int64).clip(0, self.G - 1)
        nx = tmax[:, 0] - tmin[:, 0] + 1
        ny = tmax[:, 1] - tmin[:, 1] + 1
        cnt = nx * ny
        tri = np.repeat(np.arange(m), cnt)
        k = np.arange(cnt.sum()) - np.repeat(np.cumsum(cnt) - cnt, cnt)
        cx = tmin[tri, 0] + k % nx[tri]
        cy = tmin[tri, 1] + k // nx[tri]
        cell = cy * self.G + cx
        order = np.argsort(cell, kind="stable")
        self.cell_tris = tri[order]
        cells = cell[order]
        edges = np.arange(self.G * self.G + 1)
        self.cstart = np.searchsorted(cells, edges[:-1], side="left")
        self.cend = np.searchsorted(cells, edges[:-1], side="right")

    def hidden(self, pts3: np.ndarray, eps: float, depth_max: float = math.inf) -> np.ndarray:
        """True where a triangle covers the point closer to the viewer.

        depth_max ignores triangle surface above that depth (the plan view
        uses it to remove everything above the cut plane).
        """
        n = len(pts3)
        res = np.zeros(n, dtype=bool)
        if n == 0 or self.m == 0:
            return res
        P = np.stack([pts3 @ self.u, pts3 @ self.v], axis=-1)
        Pz = pts3 @ self.w
        ci = np.floor((P - self.lo) / self.cs).astype(np.int64)
        valid = np.all((ci >= 0) & (ci < self.G), axis=1)
        idx = np.nonzero(valid)[0]
        cell = ci[idx, 1] * self.G + ci[idx, 0]
        order = np.argsort(cell, kind="stable")
        idx, cell = idx[order], cell[order]
        uniq, starts = np.unique(cell, return_index=True)
        ends = np.append(starts[1:], len(cell))
        tol = 1e-7
        for cval, s, e in zip(uniq, starts, ends):
            ts, te = self.cstart[cval], self.cend[cval]
            if ts == te:
                continue
            tri = self.cell_tris[ts:te]
            a, v0, v1, den = self.a[tri], self.v0[tri], self.v1[tri], self.den[tri]
            za, dzb, dzc = self.za[tri], self.dzb[tri], self.dzc[tri]
            pts = idx[s:e]
            for c0 in range(0, len(pts), 256):
                pi = pts[c0:c0 + 256]
                r = P[pi][:, None, :] - a[None]
                bs = (r[..., 0] * v1[:, 1] - v1[:, 0] * r[..., 1]) / den
                bt = (v0[:, 0] * r[..., 1] - r[..., 0] * v0[:, 1]) / den
                inside = (bs > tol) & (bt > tol) & (bs + bt < 1 - tol)
                depth = za + bs * dzb + bt * dzc
                res[pi] = np.any(inside & (depth > Pz[pi][:, None] + eps) & (depth < depth_max), axis=1)
        return res


def feature_edges(mesh: trimesh.Trimesh, d) -> np.ndarray:
    """Crease edges (dihedral > CREASE_DEG) and silhouette edges, as (k, 2, 3)."""
    if len(mesh.faces) == 0 or len(mesh.face_adjacency) == 0:
        return np.zeros((0, 2, 3))
    adj = mesh.face_adjacency
    facing = mesh.face_normals @ (-_vec(d)) > 1e-6
    crease = mesh.face_adjacency_angles > math.radians(CREASE_DEG)
    silhouette = facing[adj[:, 0]] != facing[adj[:, 1]]
    sel = crease | silhouette
    return mesh.vertices[mesh.face_adjacency_edges[sel]]


def split_by_visibility(segs3: np.ndarray, hidden_fn, step: float):
    """Cut each 3D edge into pieces, test each piece's midpoint, merge runs.

    Returns (visible, hidden) lists of 3D segments as (k, 2, 3) arrays.
    """
    if len(segs3) == 0:
        return np.zeros((0, 2, 3)), np.zeros((0, 2, 3))
    A, B = segs3[:, 0], segs3[:, 1]
    length = np.linalg.norm(B - A, axis=1)
    n = np.clip(np.ceil(length / step), 1, 80).astype(np.int64)
    rep = np.repeat(np.arange(len(segs3)), n)
    k = np.arange(n.sum()) - np.repeat(np.cumsum(n) - n, n)
    t0 = k / n[rep]
    t1 = (k + 1) / n[rep]
    Ar, Br = A[rep], B[rep]
    mid = Ar + (Br - Ar) * ((t0 + t1) / 2)[:, None]
    hid = hidden_fn(mid)
    brk = np.ones(len(rep), dtype=bool)
    brk[1:] = (rep[1:] != rep[:-1]) | (hid[1:] != hid[:-1])
    starts = np.nonzero(brk)[0]
    ends = np.append(starts[1:], len(rep)) - 1
    p0 = Ar[starts] + (Br[starts] - Ar[starts]) * t0[starts][:, None]
    p1 = Ar[ends] + (Br[ends] - Ar[ends]) * t1[ends][:, None]
    segs = np.stack([p0, p1], axis=1)
    h = hid[starts]
    return segs[~h], segs[h]


def project(segs3: np.ndarray, u, v) -> np.ndarray:
    """(k, 2, 3) -> (k, 4) as u0, v0, u1, v1; drops segments that project to a point."""
    if len(segs3) == 0:
        return np.zeros((0, 4))
    u, v = _vec(u), _vec(v)
    out = np.column_stack([segs3[:, 0] @ u, segs3[:, 0] @ v, segs3[:, 1] @ u, segs3[:, 1] @ v])
    keep = np.hypot(out[:, 2] - out[:, 0], out[:, 3] - out[:, 1]) > 1e-6
    out = np.round(out[keep], 4)
    return np.unique(out, axis=0) if len(out) else out


def section_polygons(mesh: trimesh.Trimesh, z: float):
    """Material cut by the plane Z = z, as a shapely geometry in (x, y)."""
    lines = trimesh.intersections.mesh_plane(mesh, plane_normal=[0, 0, 1], plane_origin=[0, 0, z])
    if len(lines) == 0:
        return Polygon()
    segs = [LineString(np.round(s[:, :2], 5)) for s in lines if np.linalg.norm(s[1, :2] - s[0, :2]) > 1e-7]
    faces = list(polygonize(unary_union(segs)))
    tris = mesh.triangles
    keep = []
    for f in faces:
        if f.area < 1e-6:
            continue
        p = f.representative_point()
        if _ray_crossings(tris, p.x, p.y, z) % 2 == 1:   # odd crossings upward: inside the solid
            keep.append(f)
    return unary_union(keep) if keep else Polygon()


def _ray_crossings(tris: np.ndarray, x: float, y: float, z: float) -> int:
    a, b, c = tris[:, 0], tris[:, 1], tris[:, 2]
    v0, v1 = (b - a)[:, :2], (c - a)[:, :2]
    den = v0[:, 0] * v1[:, 1] - v1[:, 0] * v0[:, 1]
    ok = np.abs(den) > 1e-12
    a, b, c, v0, v1, den = a[ok], b[ok], c[ok], v0[ok], v1[ok], den[ok]
    r = np.array([x, y]) - a[:, :2]
    s = (r[:, 0] * v1[:, 1] - v1[:, 0] * r[:, 1]) / den
    t = (v0[:, 0] * r[:, 1] - r[:, 0] * v0[:, 1]) / den
    inside = (s >= 0) & (t >= 0) & (s + t <= 1)
    zz = a[:, 2] + s * (b[:, 2] - a[:, 2]) + t * (c[:, 2] - a[:, 2])
    return int(np.count_nonzero(inside & (zz > z)))


def clip_below(segs3: np.ndarray, z: float) -> np.ndarray:
    """Keep the parts of 3D segments with Z <= z."""
    if len(segs3) == 0:
        return segs3
    A, B = segs3[:, 0].copy(), segs3[:, 1].copy()
    a_in, b_in = A[:, 2] <= z, B[:, 2] <= z
    keep = a_in | b_in
    cross = a_in ^ b_in
    dz = B[:, 2] - A[:, 2]
    t = np.where(cross, (z - A[:, 2]) / np.where(dz == 0, 1, dz), 0.0)
    P = A + (B - A) * t[:, None]
    A = np.where((cross & ~a_in)[:, None], P, A)
    B = np.where((cross & ~b_in)[:, None], P, B)
    return np.stack([A, B], axis=1)[keep]


def _avoid_vertex_heights(mesh: trimesh.Trimesh, z: float) -> float:
    zs = mesh.vertices[:, 2]
    for _ in range(20):
        if np.min(np.abs(zs - z)) > 1e-4:
            return z
        z += 1.37e-3
    return z


# --------------------------------------------------------------------------
# views
# --------------------------------------------------------------------------
class View:
    def __init__(self, name, title, vis, hid, bounds, section=None, note=""):
        self.name, self.title = name, title
        self.vis, self.hid = vis, hid          # (k, 4) in model mm, (u, v)
        self.bounds = bounds                    # umin, vmin, umax, vmax
        self.section = section                  # shapely geometry or None
        self.note = note
        self.dims = []                          # filled later
        self.marks = []                         # error markers (u, v)

    @property
    def size(self):
        b = self.bounds
        return b[2] - b[0], b[3] - b[1]

    def all_segments(self) -> np.ndarray:
        parts = [self.vis, self.hid]
        if self.section is not None and not self.section.is_empty:
            for poly in getattr(self.section, "geoms", [self.section]):
                for ring in [poly.exterior, *poly.interiors]:
                    c = np.asarray(ring.coords)
                    parts.append(np.column_stack([c[:-1], c[1:]]))
        parts = [p for p in parts if len(p)]
        return np.vstack(parts) if parts else np.zeros((0, 4))


def build_views(mesh: trimesh.Trimesh, cut_z: float):
    diag = float(np.linalg.norm(mesh.extents))
    step = max(diag / 250.0, 0.1)
    eps = max(diag * 1e-5, 1e-5)
    views = {}
    for name in ("front", "side", "top"):
        cfg = VIEWS[name]
        u, v = _vec(cfg["u"]), _vec(cfg["v"])
        occ = Occluder(mesh.triangles, cfg["d"], u, v)
        vis3, hid3 = split_by_visibility(feature_edges(mesh, cfg["d"]), lambda p: occ.hidden(p, eps), step)
        pu, pv = mesh.vertices @ u, mesh.vertices @ v
        views[name] = View(name, cfg["title"], project(vis3, u, v), project(hid3, u, v),
                           (pu.min(), pv.min(), pu.max(), pv.max()))

    cfg = VIEWS["plan"]
    u, v = _vec(cfg["u"]), _vec(cfg["v"])
    lo, hi = mesh.bounds
    cut = _avoid_vertex_heights(mesh, cut_z)
    section = section_polygons(mesh, cut)
    vis = np.zeros((0, 4))
    if lo[2] < cut < hi[2]:
        # everything above the cut is removed: occluders only count below it,
        # and the cut face itself (the section) hides what lies under it
        occ = Occluder(mesh.triangles, cfg["d"], u, v)

        def hidden(p):
            h = occ.hidden(p, eps, depth_max=cut)
            if not section.is_empty:
                under = p[:, 2] < cut - eps
                h |= under & shapely.contains_xy(section, p[:, 0], p[:, 1])
            return h

        edges = clip_below(feature_edges(mesh, cfg["d"]), cut)
        vis3, _ = split_by_visibility(edges, hidden, step)
        vis = project(vis3, u, v)
    views["plan"] = View("plan", f"PLAN VIEW (SECTION AT Z = {cut_z:g})", vis, np.zeros((0, 4)),
                         views["top"].bounds, section=section)
    if section.is_empty:
        views["plan"].note = "cut plane misses the part"
    return views


# --------------------------------------------------------------------------
# spec checks
# --------------------------------------------------------------------------
def _tol_value(tol) -> float:
    """'+-0.2', '±0.1', 0.2, '+0.2/-0.0' -> the largest number found; default when absent."""
    if tol is None:
        return DEFAULT_VALUE_TOL
    if isinstance(tol, (int, float)):
        return abs(float(tol))
    nums = [abs(float(x)) for x in re.findall(r"\d+(?:\.\d+)?", str(tol))]
    return max(nums) if nums else DEFAULT_VALUE_TOL


def _dist_to_segments(p, segs: np.ndarray) -> float:
    if len(segs) == 0:
        return math.inf
    a, b = segs[:, :2], segs[:, 2:]
    ab = b - a
    L2 = np.einsum("ij,ij->i", ab, ab)
    t = np.clip(np.einsum("ij,ij->i", np.asarray(p) - a, ab) / np.where(L2 > 0, L2, 1), 0, 1)
    proj = a + ab * t[:, None]
    return float(np.min(np.hypot(*(proj - np.asarray(p)).T)))


def check_envelope(spec: dict, mesh: trimesh.Trimesh, errors: list, checks: list):
    env = spec.get("envelope") or {}
    tol = float(env.get("tolerance", 0.5))
    for i, axis in enumerate("xyz"):
        if axis not in env or env[axis] in (None, ""):
            continue
        want, got = float(env[axis]), float(mesh.extents[i])
        ok = abs(want - got) <= tol
        checks.append({"check": f"envelope {axis.upper()}", "spec": want, "model": round(got, 3), "tol": tol, "ok": ok})
        if not ok:
            errors.append(f"envelope {axis.upper()}: model {got:.2f} mm, spec {want:g} +- {tol:g} mm")


def apply_annotations(spec: dict, views: dict, errors: list, checks: list):
    dims_by_id = {d.get("id"): d for d in spec.get("dimensions", []) if isinstance(d, dict)}
    for i, ann in enumerate((spec.get("drawing") or {}).get("dimensions", []) or []):
        if not isinstance(ann, dict):
            continue
        vname = ann.get("view")
        if vname not in views:
            errors.append(f"drawing.dimensions[{i}]: unknown view {vname!r} (front, side, top, plan)")
            continue
        view = views[vname]
        cfg = VIEWS[vname]
        u, v = _vec(cfg["u"]), _vec(cfg["v"])
        did = ann.get("id")
        sd = dims_by_id.get(did) if did else None
        label_id = f"{did} " if did else ""
        segs = view.all_segments()
        kind = ann.get("type", "linear")
        if kind == "diameter":
            try:
                c3 = _vec(ann["center"])
                d = float(ann.get("d", sd.get("value") if sd else None))
            except (KeyError, TypeError, ValueError):
                errors.append(f"drawing.dimensions[{i}]: diameter needs 'center' [x,y,z] and 'd' (or an id with a value)")
                continue
            c2 = np.array([c3 @ u, c3 @ v])
            r = d / 2
            misses = [a for a in np.linspace(0, 2 * math.pi, 12, endpoint=False)
                      if _dist_to_segments(c2 + r * np.array([math.cos(a), math.sin(a)]), segs) > ON_GEOMETRY_TOL]
            ok = len(misses) <= 2   # a leader or a seam may cut a couple of samples
            name = f"{label_id}diameter {d:g} in {vname}"
            checks.append({"check": name, "model_edges_at_radius": ok, "ok": ok})
            if not ok:
                errors.append(f"{name}: no circular edge of that size around {[float(x) for x in c3]} in the {vname} view")
            view.dims.append(dict(type="diameter", c=c2, d=d, label=f"{label_id}⌀{d:g}", ok=ok))
            continue

        try:
            p1, p2 = _vec(ann["from"]), _vec(ann["to"])
        except (KeyError, TypeError, ValueError):
            errors.append(f"drawing.dimensions[{i}]: linear needs 'from' and 'to' as [x,y,z]")
            continue
        a2, b2 = np.array([p1 @ u, p1 @ v]), np.array([p2 @ u, p2 @ v])
        orient = ann.get("orient")
        if orient not in ("horizontal", "vertical", "aligned"):
            du, dv = abs(b2[0] - a2[0]), abs(b2[1] - a2[1])
            orient = "horizontal" if dv < 1e-6 else "vertical" if du < 1e-6 else "aligned"
        if orient == "horizontal":
            measured = abs(b2[0] - a2[0])
        elif orient == "vertical":
            measured = abs(b2[1] - a2[1])
        else:
            measured = float(np.hypot(*(b2 - a2)))
        ok = True
        expect = ann.get("expect", sd.get("value") if sd else None)
        entry = {"check": f"{label_id}{vname} {orient}".strip(), "measured": round(measured, 3)}
        if expect is not None:
            tol = _tol_value(ann.get("tol", sd.get("tol") if sd else None))
            entry.update(expect=float(expect), tol=tol)
            if abs(measured - float(expect)) > tol + 1e-9:
                ok = False
                errors.append(f"{entry['check']}: annotation spans {measured:.3f} mm, spec says {float(expect):g} +- {tol:g}")
        if ann.get("on_geometry", True):
            for tag, pt in (("from", a2), ("to", b2)):
                dist = _dist_to_segments(pt, segs)
                if dist > ON_GEOMETRY_TOL:
                    ok = False
                    view.marks.append(pt)
                    errors.append(f"{entry['check']}: '{tag}' point {list(map(float, (p1 if tag == 'from' else p2)))} "
                                  f"is {dist:.2f} mm from any model edge in the {vname} view")
        entry["ok"] = ok
        checks.append(entry)
        text = f"{label_id}{measured:.2f}".rstrip("0").rstrip(".")
        if expect is not None and not ok:
            text += f" (spec {float(expect):g})"
        view.dims.append(dict(type="linear", a=a2, b=b2, orient=orient, offset=float(ann.get("offset", DEFAULT_DIM_OFFSET)),
                              label=text, ok=ok))


# --------------------------------------------------------------------------
# SVG
# --------------------------------------------------------------------------
def svg_defs() -> str:
    return (
        "<defs>"
        '<pattern id="hatch" patternUnits="userSpaceOnUse" width="1.6" height="1.6" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="1.6" stroke="{COL_LINE}" stroke-width="0.18"/></pattern>'
        f'<marker id="arr" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="3" markerHeight="3" '
        f'orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,1.5 L10,5 L0,8.5 z" fill="{COL_DIM}"/></marker>'
        f'<marker id="arr-err" viewBox="0 0 10 10" refX="10" refY="5" markerWidth="3" markerHeight="3" '
        f'orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path d="M0,1.5 L10,5 L0,8.5 z" fill="{COL_ERR}"/></marker>'
        "</defs>"
        "<style>text{font-family:Arial,Helvetica,sans-serif}"
        f".vis{{stroke:{COL_LINE};stroke-width:0.5;stroke-linecap:round;fill:none}}"
        f".hid{{stroke:{COL_HIDDEN};stroke-width:0.25;stroke-dasharray:1.6 0.8;fill:none}}"
        f".cut{{stroke:{COL_LINE};stroke-width:0.7;fill:url(#hatch);fill-rule:evenodd}}"
        f".dim{{stroke:{COL_DIM};stroke-width:0.18;fill:none}}"
        f".dimerr{{stroke:{COL_ERR};stroke-width:0.25;fill:none}}"
        ".dt{paint-order:stroke;stroke:#fff;stroke-width:0.8;stroke-linejoin:round}"
        "</style>"
    )


def _f(x: float) -> str:
    return f"{x:.3f}".rstrip("0").rstrip(".")


def _segs_path(segs: np.ndarray, X, Y) -> str:
    return " ".join(f"M{_f(X(a))} {_f(Y(b))}L{_f(X(c))} {_f(Y(d))}" for a, b, c, d in segs)


def _dim_linear(P1, P2, orient: str, offset: float, label: str, ok: bool, level=None) -> str:
    """Dimension between paper points P1, P2.

    The dimension line sits `offset` paper mm beyond the farther point (+ = below /
    right), or at the absolute paper coordinate `level` along the normal when given.
    Text sits above the line (ISO: readable from the bottom or the right).
    """
    P1, P2 = np.asarray(P1, float), np.asarray(P2, float)
    if orient == "horizontal":
        e = np.array([1.0, 0.0])
    elif orient == "vertical":
        e = np.array([0.0, 1.0])
    else:
        dvec = P2 - P1
        e = dvec / (np.linalg.norm(dvec) or 1.0)
    n = np.array([-e[1], e[0]])
    if n[0] < 0 or (abs(n[0]) < 1e-9 and n[1] < 0):
        n = -n                                    # n points right / down
    k1, k2 = P1 @ n, P2 @ n
    if level is None:
        level = (max(k1, k2) + offset) if offset >= 0 else (min(k1, k2) + offset)
    A = P1 + n * (level - k1)
    B = P2 + n * (level - k2)
    cls, mk, col = ("dim", "arr", COL_DIM) if ok else ("dimerr", "arr-err", COL_ERR)
    out = []
    for P, Q in ((P1, A), (P2, B)):
        gap = Q - P
        dist = float(np.linalg.norm(gap))
        if dist > 1.2:
            g = gap / dist
            s = P + g * 1.0          # small gap at the part
            t = Q + g * 1.5          # overshoot past the dimension line
            out.append(f'<path class="{cls}" d="M{_f(s[0])} {_f(s[1])}L{_f(t[0])} {_f(t[1])}"/>')
    out.append(f'<path class="{cls}" marker-start="url(#{mk})" marker-end="url(#{mk})" '
               f'd="M{_f(A[0])} {_f(A[1])}L{_f(B[0])} {_f(B[1])}"/>')
    mid = (A + B) / 2
    ang = math.degrees(math.atan2(B[1] - A[1], B[0] - A[0]))
    if ang >= 90:
        ang -= 180
    elif ang < -90:
        ang += 180
    up = np.array([math.sin(math.radians(ang)), -math.cos(math.radians(ang))])
    tp = mid + up * 0.9
    out.append(f'<text class="dt" x="{_f(tp[0])}" y="{_f(tp[1])}" font-size="{TEXT}" fill="{col}" text-anchor="middle" '
               f'transform="rotate({_f(ang)} {_f(tp[0])} {_f(tp[1])})">{escape(label)}</text>')
    return "".join(out)


def _dim_diameter(C, r_paper: float, label: str, ok: bool) -> str:
    cls, mk, col = ("dim", "arr", COL_DIM) if ok else ("dimerr", "arr-err", COL_ERR)
    d = np.array([math.cos(math.radians(-45)), math.sin(math.radians(-45))])
    edge = C + d * r_paper
    knee = C + d * (r_paper + 7)
    tail = knee + np.array([3 + len(label) * TEXT * 0.55, 0])
    s = 1.2
    return (f'<path class="{cls}" d="M{_f(C[0]-s)} {_f(C[1])}L{_f(C[0]+s)} {_f(C[1])}M{_f(C[0])} {_f(C[1]-s)}L{_f(C[0])} {_f(C[1]+s)}"/>'
            f'<path class="{cls}" marker-start="url(#{mk})" d="M{_f(edge[0])} {_f(edge[1])}L{_f(knee[0])} {_f(knee[1])}L{_f(tail[0])} {_f(tail[1])}"/>'
            f'<text class="dt" x="{_f(knee[0] + 1.5)}" y="{_f(knee[1] - 0.9)}" font-size="{TEXT}" fill="{col}">{escape(label)}</text>')


AUTO_DIM_OFFSET = 8.0                 # overall-size dimensions, paper mm outside the view
DEFAULT_DIM_OFFSET = 16.0             # custom dimensions stack outside the auto ones


def view_margins(view: "View"):
    """Paper mm needed around the view outline: (left, top, right, bottom), title included."""
    pad = TEXT + 2.5
    left, top_dims, right, bottom = 0.0, 0.0, AUTO_DIM_OFFSET + 3.0, AUTO_DIM_OFFSET + 3.0
    for dm in view.dims:
        if dm["type"] != "linear" or dm["orient"] == "aligned":
            continue
        o = dm["offset"]
        if dm["orient"] == "horizontal":
            if o >= 0:
                bottom = max(bottom, o + 3.0)
            else:
                top_dims = max(top_dims, -o + pad)
        else:
            if o >= 0:
                right = max(right, o + 3.0)
            else:
                left = max(left, -o + pad)
    return left, top_dims + LABEL_H, right, bottom


def view_group(view: View, s: float, ox: float, oy: float, auto_dims: bool = True) -> str:
    """SVG for one view; (ox, oy) is the paper position of the view's top-left corner."""
    umin, vmin, umax, vmax = view.bounds

    def X(u): return ox + (u - umin) * s
    def Y(v): return oy + (vmax - v) * s

    out = [f'<g id="view-{view.name}">']
    w, h = (umax - umin) * s, (vmax - vmin) * s
    title_y = oy - (view_margins(view)[1] - LABEL_H) - 4
    out.append(f'<text x="{_f(ox + w / 2)}" y="{_f(title_y)}" font-size="{TEXT}" font-weight="bold" '
               f'text-anchor="middle">{escape(view.title)}</text>')
    if view.section is not None and not view.section.is_empty:
        d = []
        for poly in getattr(view.section, "geoms", [view.section]):
            for ring in [poly.exterior, *poly.interiors]:
                c = list(ring.coords)
                d.append("M" + "L".join(f"{_f(X(a))} {_f(Y(b))}" for a, b in c) + "Z")
        out.append(f'<path class="cut" d="{" ".join(d)}"/>')
    if len(view.hid):
        out.append(f'<path class="hid" d="{_segs_path(view.hid, X, Y)}"/>')
    if len(view.vis):
        out.append(f'<path class="vis" d="{_segs_path(view.vis, X, Y)}"/>')
    if view.note:
        out.append(f'<text x="{_f(ox + w / 2)}" y="{_f(oy + h / 2)}" font-size="{TEXT}" fill="{COL_ERR}" '
                   f'text-anchor="middle">{escape(view.note)}</text>')
    def fmt(x): return f"{x:.2f}".rstrip("0").rstrip(".")

    if auto_dims and w > 0 and h > 0:
        out.append(_dim_linear((ox, oy + h), (ox + w, oy + h), "horizontal", 0, fmt(umax - umin), True,
                               level=oy + h + AUTO_DIM_OFFSET))
        out.append(_dim_linear((ox + w, oy + h), (ox + w, oy), "vertical", 0, fmt(vmax - vmin), True,
                               level=ox + w + AUTO_DIM_OFFSET))
    for dm in view.dims:
        if dm["type"] == "diameter":
            out.append(_dim_diameter(np.array([X(dm["c"][0]), Y(dm["c"][1])]), dm["d"] / 2 * s, dm["label"], dm["ok"]))
            continue
        P1 = (X(dm["a"][0]), Y(dm["a"][1]))
        P2 = (X(dm["b"][0]), Y(dm["b"][1]))
        o = dm["offset"]
        level = None                       # offsets count from the view outline, like CAD
        if dm["orient"] == "horizontal":
            level = oy + h + o if o >= 0 else oy + o
        elif dm["orient"] == "vertical":
            level = ox + w + o if o >= 0 else ox + o
        out.append(_dim_linear(P1, P2, dm["orient"], o, dm["label"], dm["ok"], level=level))
    for m in view.marks:
        out.append(f'<circle cx="{_f(X(m[0]))}" cy="{_f(Y(m[1]))}" r="1.6" fill="none" stroke="{COL_ERR}" stroke-width="0.4"/>')
    out.append("</g>")
    return "".join(out)


def scale_label(ratio) -> str:
    return f"{ratio[0]}:{ratio[1]}"


def sheet_layout(views: dict, s: float):
    """Third-angle grid: [top | plan] over [front | side]. Returns positions and fit."""
    m = {n: view_margins(v) for n, v in views.items()}
    X, Y = views["top"].size[0] * s, views["top"].size[1] * s
    Z = views["front"].size[1] * s
    SY, PX = views["side"].size[0] * s, views["plan"].size[0] * s
    c1_left = max(m["top"][0], m["front"][0])
    c1_right = max(m["top"][2], m["front"][2])
    c2_left = max(m["plan"][0], m["side"][0])
    c2_right = max(m["plan"][2], m["side"][2])
    r1_top = max(m["top"][1], m["plan"][1])
    r1_bottom = max(m["top"][3], m["plan"][3])
    r2_top = max(m["front"][1], m["side"][1])
    r2_bottom = max(m["front"][3], m["side"][3])
    x1 = BORDER + 6 + c1_left
    x2 = x1 + X + c1_right + CELL_GAP + c2_left
    y1 = BORDER + 6 + r1_top
    y2 = y1 + Y + r1_bottom + r2_top
    right = x2 + max(SY, PX) + c2_right
    bottom = y2 + Z + r2_bottom
    fits = right <= SHEET_W - BORDER - 4 and bottom <= SHEET_H - BORDER - TITLE_H - 4
    return {"top": (x1, y1), "plan": (x2, y1), "front": (x1, y2), "side": (x2, y2)}, fits


def choose_scale(views: dict):
    for ratio in SCALES:
        s = ratio[0] / ratio[1]
        if sheet_layout(views, s)[1]:
            return s, scale_label(ratio)
    s = 1 / 100
    while not sheet_layout(views, s)[1] and s > 1e-4:
        s /= 1.25
    return s, f"1:{1 / s:.0f}"


def standalone_svg(view: View, s: float) -> str:
    w, h = view.size[0] * s, view.size[1] * s
    ml, mt, mr, mb = view_margins(view)
    pad_l, pad_t = ml + 8, mt + 6
    W, H = pad_l + w + mr + 8 + (30 if any(d["type"] == "diameter" for d in view.dims) else 0), pad_t + h + mb + 8
    body = view_group(view, s, pad_l, pad_t)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{_f(W)}mm" height="{_f(H)}mm" viewBox="0 0 {_f(W)} {_f(H)}">'
            f'{svg_defs()}<rect width="100%" height="100%" fill="#fff"/>{body}</svg>\n')


def sheet_svg(views: dict, s: float, scale_txt: str, spec: dict, parts: list, errors: list, mesh) -> str:
    pos, _ = sheet_layout(views, s)
    body = [view_group(views[n], s, *pos[n]) for n in ("top", "plan", "front", "side")]
    # third-angle symbol is described in text; title block bottom-right
    tb_w, tb_x, tb_y = 190.0, SHEET_W - BORDER - 190.0, SHEET_H - BORDER - TITLE_H
    project = str(spec.get("project") or "untitled")
    status = str(spec.get("status") or "draft")
    rev = str(spec.get("revision", "-"))
    size = " x ".join(f"{v:.2f}".rstrip("0").rstrip(".") for v in mesh.extents)
    names = ", ".join(p[0] for p in parts)
    rows = [
        ("PROJECT", project), ("PARTS", names), ("ENVELOPE (X x Y x Z)", f"{size} mm"),
        ("SCALE", scale_txt), ("UNITS", "mm"), ("PROJECTION", "third angle"),
        ("SPEC", f"rev {rev}, {status}"), ("DATE", dt.date.today().isoformat()),
    ]
    tb = [f'<rect x="{_f(tb_x)}" y="{_f(tb_y)}" width="{_f(tb_w)}" height="{_f(TITLE_H)}" fill="#fff" stroke="{COL_LINE}" stroke-width="0.5"/>']
    for i, (k, val) in enumerate(rows):
        cx = tb_x + (i % 2) * tb_w / 2
        cy = tb_y + (i // 2) * TITLE_H / 4
        tb.append(f'<rect x="{_f(cx)}" y="{_f(cy)}" width="{_f(tb_w / 2)}" height="{_f(TITLE_H / 4)}" fill="none" stroke="{COL_LINE}" stroke-width="0.25"/>')
        tb.append(f'<text x="{_f(cx + 1.5)}" y="{_f(cy + 3.2)}" font-size="2.2" fill="#666">{escape(k)}</text>')
        tb.append(f'<text x="{_f(cx + 1.5)}" y="{_f(cy + 8.6)}" font-size="3.2">{escape(val[:48])}</text>')
    notes = [f'<text x="{_f(BORDER + 4)}" y="{_f(SHEET_H - BORDER - TITLE_H + 4)}" font-size="2.8" font-weight="bold">NOTES</text>']
    lines = ["All dimensions in mm. Model coordinates: Z up, part front faces -Y.",
             "Hidden edges dashed. Plan view: horizontal section, cut material hatched."]
    lines += [f"ERROR: {e}" for e in errors[:7]]
    if len(errors) > 7:
        lines.append(f"... and {len(errors) - 7} more errors (see drawings.json)")
    for i, ln in enumerate(lines):
        col = COL_ERR if ln.startswith("ERROR") else COL_LINE
        notes.append(f'<text x="{_f(BORDER + 4)}" y="{_f(SHEET_H - BORDER - TITLE_H + 9 + i * 4.2)}" font-size="2.6" '
                     f'fill="{col}">{escape(ln[:110])}</text>')
    frame = (f'<rect x="{BORDER}" y="{BORDER}" width="{SHEET_W - 2 * BORDER}" height="{SHEET_H - 2 * BORDER}" '
             f'fill="none" stroke="{COL_LINE}" stroke-width="0.7"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{SHEET_W}mm" height="{SHEET_H}mm" '
            f'viewBox="0 0 {SHEET_W} {SHEET_H}">{svg_defs()}<rect width="100%" height="100%" fill="#fff"/>'
            f'{frame}{"".join(body)}{"".join(notes)}{"".join(tb)}</svg>\n')


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def load_parts(model_dir: Path):
    parts = []
    for stl in sorted(model_dir.glob("*.stl")):
        mesh = trimesh.load(str(stl), file_type="stl", force="mesh")
        meta_path = stl.with_suffix(".json")
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.is_file() else {}
        parts.append((stl.stem, mesh, meta))
    return parts


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Front/side/top elevations and plan view of a design-pipeline model.")
    ap.add_argument("project", help="project folder (projects/<name>)")
    ap.add_argument("--cut-z", type=float, default=None, help="plan view cut height in mm (default: spec, else mid height)")
    args = ap.parse_args(argv)

    project = Path(args.project).resolve()
    processed = project / "processed"
    model_dir = processed / "model"
    out_dir = processed / "drawings"
    spec_path = processed / "spec.json"
    spec = {}
    if spec_path.is_file():
        try:
            spec = json.loads(spec_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            print(f"spec.json is not valid JSON: {exc}", file=sys.stderr)
            return 2
    parts = load_parts(model_dir)
    if not parts:
        print(f"no STL in {model_dir}: run the build step first", file=sys.stderr)
        return 2
    mesh = trimesh.util.concatenate([p[1] for p in parts])

    lo, hi = mesh.bounds
    cut_z = args.cut_z
    if cut_z is None:
        cut_z = (spec.get("drawing") or {}).get("plan_cut_z")
    cut_z = float(cut_z) if cut_z is not None else float((lo[2] + hi[2]) / 2)

    views = build_views(mesh, cut_z)
    errors, checks = [], []
    check_envelope(spec, mesh, errors, checks)
    apply_annotations(spec, views, errors, checks)
    s, scale_txt = choose_scale(views)

    out_dir.mkdir(parents=True, exist_ok=True)
    for name, view in views.items():
        (out_dir / f"{name}.svg").write_text(standalone_svg(view, s), encoding="utf-8")
    (out_dir / "sheet.svg").write_text(sheet_svg(views, s, scale_txt, spec, parts, errors, mesh), encoding="utf-8")
    report = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "scale": scale_txt,
        "plan_cut_z": cut_z,
        "bbox": {"min": [round(float(x), 3) for x in lo], "max": [round(float(x), 3) for x in hi],
                 "size": [round(float(x), 3) for x in mesh.extents]},
        "parts": [p[0] for p in parts],
        "views": {n: {"visible_edges": int(len(v.vis)), "hidden_edges": int(len(v.hid))} for n, v in views.items()},
        "checks": checks,
        "errors": errors,
        "ok": not errors,
    }
    (out_dir / "drawings.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"drawings at scale {scale_txt}: {', '.join(f'{n}.svg' for n in views)} + sheet.svg in {out_dir}")
    for c in checks:
        print(("  ok    " if c["ok"] else "  FAIL  ") + json.dumps(c))
    if errors:
        print(f"\n{len(errors)} drawing check error(s):", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
