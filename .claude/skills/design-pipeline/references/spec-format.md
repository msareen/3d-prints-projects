# spec.json format (`design-pipeline/spec@1`)

`pipeline.py check` validates it, and `build` / `finalize` run the same check.
All lengths are in mm, and all positions are model coordinates from the datum
(Z up, print orientation, front faces -Y).

```jsonc
{
  "schema": "design-pipeline/spec@1",
  "project": "wall-hook",               // = folder name under projects/
  "status": "draft",                    // draft | confirmed (only the user confirms)
  "revision": 1,                        // bump on every change after confirmation
  "units": "mm",                        // always mm
  "summary": "Single hook for a 30 mm towel ring, screwed to a wall ...",
  "inputs": [
    {"file": "input/sketch.jpg", "kind": "sketch", "notes": "side view with 5 callouts"}
  ],
  "datum": {
    "origin": "centre of the back plate, on its bed face",
    "x": "along the plate width, left to right seen from the front",
    "y": "towards the back (front faces -Y)",
    "z": "up = print direction; the part sits on Z = 0"
  },
  "envelope": {"x": 40, "y": 35, "z": 60, "tolerance": 0.5},   // overall model size, checked by `draw`
  "print": {                            // the same values as in build.py: `check` compares them
    "printer_bed": [220, 220, 250],     // -> PRINTER_BED
    "nozzle": 0.4,                      // -> NOZZLE
    "layer": 0.2,                       // -> LAYER
    "material": "PETG",                 // -> MATERIAL (the primary material)
    "materials": ["PETG", "PLA"],       // optional: one output/<MAT>/ release each; [0] == material
    "supports": false,                  // -> SUPPORTS_ALLOWED
    "orientation": "back plate flat on the bed, hook pointing up",
    "quantity": 2
  },
  "parts": [{"name": "wall-hook", "description": "one piece"}],
  "dimensions": [
    {
      "id": "D1",                       // D + number, unique, never reused
      "name": "plate width",
      "value": 40.0,                    // mm, number
      "tol": "±0.3",                    // optional: number or text; the largest number is used
      "material_values": {"PLA": 0.4},  // optional: this size for a secondary material (needs param)
      "basis": "measured",              // given | measured | derived | estimated | default
      "confidence": "high",             // high | medium | low
      "critical": false,
      "source": "input/sketch.jpg: callout '40' across the plate, top edge",
      "fit": null,                      // press | snug | sliding | free for mating sizes
      "param": "PLATE_W"                // optional: the build.py name that must equal `value`
    }
  ],
  "features": [
    {"id": "F1", "name": "countersunk screw hole", "count": 2,
     "position": "x = 0, z = 12 and z = 48 (on the centre line)",
     "dims": ["D4", "D5"], "notes": "through the plate, countersink on the front face"}
  ],
  "assumptions": ["A1: plate corners R3 (not shown in the sketch) ..."],
  "open_questions": [
    {"id": "Q1", "question": "Is the 30 mm the ring's outer or wire diameter?", "blocking": true, "answer": null}
  ],
  "drawing": {
    "plan_cut_z": 2.0,                  // plan-view section height; null = mid height
    "dimensions": [ /* annotations: see drawings.md */ ]
  }
}
```

## What `check` enforces

Always:
- unique `D<n>` ids; a numeric `value`; `basis`, `confidence` and `source`
  present and valid;
- `features[].dims` refer to existing ids;
- every `param` exists in build.py and has a **literal value equal to the
  spec value** (build.py is parsed, never executed for this check);
- `print.*` equals PRINTER_BED, NOZZLE, LAYER, MATERIAL and SUPPORTS_ALLOWED in build.py;
- every entry of `print.materials` has a profile in `materials/<MAT>.json`, and
  `print.materials[0]` equals `print.material`;
- build.py `NAME` is a valid part name.

Warnings in `draft`, which become errors once `confirmed`:
- empty summary, datum, print or parts;
- a critical dimension that is `estimated`, `default` or `confidence: low`;
- a blocking open question without an `answer`.

## Linking to build.py

Link a dimension to a parameter only when the parameter **is** that number
(`PLATE_W = 40.0  # D1 plate width (measured, sketch.jpg)`). Values that the
build derives, such as a hole diameter of `SCREW_D + 2 * CLEAR`, link the
input (`SCREW_D` to the screw-shank dimension), not the result. Put the
dimension ID first in every parameter comment, so a reader can trace each
number back to its source.
