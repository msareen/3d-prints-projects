# Stage 2 drawings: elevations, plan view, annotations

`pipeline.py draw <project>` reads `processed/model/*.stl` and writes the
following to `processed/drawings/`:

| File | View | Looking | Paper axes |
|---|---|---|---|
| `front.svg` | front elevation | along +Y (viewer at the -Y side) | X right, Z up |
| `side.svg` | right side elevation | along -X (viewer at the +X side) | Y right, Z up |
| `top.svg` | top elevation | down -Z | X right, Y up |
| `plan.svg` | plan view = horizontal **section** at `plan_cut_z` | down -Z | X right, Y up |
| `sheet.svg` | all four on A3, third-angle layout (top above front, side right of front, plan top right), title block, notes | | |
| `drawings.json` | scale, edge counts, every check, errors | | |

Visible edges are solid. Hidden edges in the elevations are dashed. In the
plan view, the material cut by the plane is hatched, and the edges below the
cut are drawn as seen from above. Every view gets its overall size
dimensioned automatically. The scale is the largest ISO scale (10:1, 5:1,
2:1, 1:1, 1:2, 1:5, ...) at which all four views fit on the sheet. Open SVGs
in a browser or in VS Code.

Choose `drawing.plan_cut_z` so the cut passes through the features that
matter (holes, slots, pockets, wall thickness). Mid height is the default and
often misses them.

## Dimension annotations (`spec.json` → `drawing.dimensions`)

Annotations do two jobs: they put the spec's key dimensions on the drawing,
and they **check the model**. Each annotation point must lie on a model edge
in that view, within 0.25 mm. If the model lacks a feature the spec
describes, or has it in the wrong place, the point lands on nothing. The
annotation is then drawn red, listed under NOTES, and `draw` exits with code
1. `finalize` refuses to release until it is fixed.

Linear:

```json
{"id": "D1", "view": "front", "from": [-20, -2, 0], "to": [20, -2, 0], "offset": 12}
```

- `from` / `to`: 3D model points [x, y, z]. Only the two in-plane coordinates
  matter for the view; the third can be anything.
- `orient`: `horizontal`, `vertical` or `aligned`. It is inferred when the
  points share a coordinate.
- `offset`: paper mm from the farther point. Positive is below (horizontal)
  or right (vertical); negative is above or left. The default is 10. Stack
  several dimensions at 10, 18, 26, ...
- `id`: the label prefix, and the expected value comes from that spec
  dimension (with its `tol`). The measured span must match.
- `expect` / `tol`: override the expected value, for example when the
  modelled size includes clearance (`"expect": 4.0` for a 3.5 shank + 2 x 0.25).
- `on_geometry: false`: skip the on-edge check, for spans that start or end
  at a centre line (hole pitch between centres).

Diameter:

```json
{"id": "D4", "view": "top", "type": "diameter", "center": [0, 0, 4], "d": 4.0}
```

The check looks for model edges all around radius d/2 from the centre in
that view.

## What to annotate

At least every **critical** dimension, in the view where it is a true length
(a size along X belongs in the front or top view, not the side view). Add the
positions of every hole or slot from the datum, and the wall thicknesses that
carry load. For hole patterns, dimension the pitch (centre to centre, with
`on_geometry: false`) and one edge to a hole edge (checked).

When an annotation fails, decide which side is wrong. Either the annotation
points are wrong (a typo in from/to), or **the model is wrong**: fix build.py.
Never move the annotation onto the model just to make the check pass.
