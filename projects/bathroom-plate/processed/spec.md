# bathroom-plate: design specification

> Status: **confirmed**, revision 2. All dimensions in mm. Machine-readable twin:
> `spec.json` (same IDs). The model is built only from what is written here.

## Revisions

- Rev 1 (draft): corner shelf, 170 x 170, 7.8 thick, PETG on the A1 mini. First draft had a soft-arc front (sagitta 28, R272); the user found it took too much space ("keep it mostly square, curve is just a very subtle, just a very small part of corner"), so it is now a square with only the front corner rounded: R30, then R40 ("increase the curve little bit make be 1cm"). D8, D9, D10 (arc) deleted; D17 added.
- Rev 2: print settings only, geometry unchanged. 100 % infill (282 g) replaced by a sandwich: 4 walls, 6/6 top/bottom layers (1.2 mm skins), 20 % gyroid, about 130 g. User: "you decide what should be the best fill with min material use, 282 is too much I need stuctural streghtn rather than make a block".

## 1. Purpose and context

A PETG plate that replaces the glass corner shelf in a shower corner
(input/brief.md). Two existing chrome D-clamp brackets hold it, one on each
wall, at the same height. The user gives the far edge of each bracket as 6 in
(152.4) from the corner (input/20261107_143349.jpg). The old glass
(input/20261107_143413.jpg) has straight edges along both walls and a full
quarter-circle front. The new plate is as large as the Bambu Lab A1 mini bed
allows with a safe margin. It stays mostly square: only the front corner gets
a subtle curve, and the other three corners are slightly rounded.

## 2. Inputs reviewed

| File | Kind | What it shows / says | Usable for |
|---|---|---|---|
| input/brief.md | text | user's words and answers | goal, size rule, curve style, D7 |
| input/20261107_123217.jpg | photo | D clamp on the wall, top; caliper over the clamp: "11.7 mm" | D2 (reference) |
| input/20261107_123228.jpg | photo | D clamp from the front (clamp screw, slot); caliper: "12.8 mm" (glare on first digit) | D2 (reference) |
| input/20261107_123245.jpg | photo | old glass edge; caliper: "7.9 mm" | D1 → D3 |
| input/20261107_143349.jpg | photo | the empty corner, one clamp per wall, symmetric | layout, D15 (estimated) |
| input/20261107_143413.jpg | photo | the glass shelf in use, from below: quarter-circle corner shelf | layout, shape |

## 3. Coordinate system and datum

- Origin: the virtual sharp wall corner of the plate, Z = 0 on the bed face.
- X: along the wall-A edge, away from the corner.
- Y: along the wall-B edge, away from the corner. The wall-A edge (Y = 0) faces -Y: the front elevation looks at it.
- Z: up, print direction; the plate lies flat, shelf face up.

## 4. Overall description

A flat, solid square plate, 170 x 170, 7.8 thick. Two edges lie along the X
and Y axes against the two walls. The front corner, diagonally opposite the
wall corner, is rounded R40 (centre at 130, 130), which takes 16.6 off the
diagonal; the old glass's quarter circle took 70. The other three corners (the
wall corner and the two wall-edge tips) are rounded R4. The plate is symmetric
about the diagonal X = Y. The top edge has an R1.2 roundover all round, and the
bottom edge a 0.4 chamfer against elephant foot. The plate is the full 170 deep
everywhere except under the front corner; at each bracket's far edge (152.4
from the corner) it is 163.1 deep.

## 5. Dimension register

| ID | Name | Value | Tol | Basis | Conf. | Crit. | Source |
|---|---|---|---|---|---|---|---|
| D1 | old glass thickness (reference) | 7.9 | ±0.1 | measured | high | | 123245.jpg caliper "7.9" |
| D2 | bracket clamp outer height (reference) | 12.8 | ±0.6 | measured | medium | | 123228.jpg "12.8"; 123217.jpg "11.7" |
| D3 | plate thickness | 7.8 | ±0.1 | derived | high | yes | D1 rounded down to 39 layers |
| D4 | printer bed X, Y | 180 | | default | high | | Bambu Lab A1 mini |
| D5 | safe margin per side | 5 | | default | high | | user: "with safe margin" |
| D6 | square side (wall-edge length) | 170 | | derived | high | | D4 - 2 x D5 |
| D7 | corner to bracket far edge | 152.4 | ±3 | given | medium | yes | user: 6 in, far edge |
| D8 | (deleted: arc sagitta, draft 1) | | | | | | |
| D9 | (deleted: arc radius, draft 1) | | | | | | |
| D10 | (deleted: arc apex, draft 1) | | | | | | |
| D11 | plate depth at X = D7 | 163.14 | ±0.3 | derived | high | | 130 + √(40² − 22.4²) |
| D12 | corner radius (other 3 corners) | 4 | | default | high | | user: "very little curve" |
| D13 | top edge roundover | 1.2 | | default | high | | design choice |
| D14 | bottom chamfer | 0.4 | | default | high | | design rules |
| D15 | bracket projection from wall | 20 | ±8 | estimated | low | | 143349.jpg, Q4 |
| D16 | overall extent X and Y | 170 | ±0.3 | derived | high | | = D6 |
| D17 | front corner radius | 40 | | default | high | | user: "very subtle, very small part of corner", then +1 cm |

## 6. Features

- F1 plate outline: square, wall edges on Y = 0 and X = 0 (D6, D11, D16).
- F2 rounded corners: front corner R40 (D17), the other three R4 (D12).
- F3 solid plate body, Z 0 to 7.8, no holes (D3).
- F4 top edge roundover R1.2 (D13).
- F5 bottom edge chamfer 0.4 (D14).

## 7. Consistency checks

- Bed: 170 x 170 ≤ 180 - 2 x 5 = 170 ✓ (printcheck: fits with 5 mm margin).
- Side 170 > bracket far edge 152.4: the plate runs 17.6 past each bracket ✓.
- Depth at the bracket far edge 163.1 > estimated bracket projection 20 (D15) ✓.
- Thickness 7.8 ≤ glass 7.9, and much less than the clamp's outer height 11.7–12.8 ✓.
- R40 front corner: diagonal loss = 40 x (√2 − 1) = 16.6 ✓.
- Drawing check: envelope 170 / 170 / 7.8, D3, D11 and D16 match the model ✓.

## 8. Print setup

Bambu Lab A1 mini (180 x 180 x 180), 0.4 nozzle, 0.2 layers, PETG, no
supports. Flat, shelf face up, on textured PEI. One plate, sandwich print: 4 walls, 6/6 top/bottom layers, **20 % gyroid**.
About 130 g.

## 9. Assumptions

- A1: 90° corner; both brackets at the same height and distance from the corner.
- A2: the brackets clamp the plate edge with their screws; no holes or tabs.
- A3: symmetric about the diagonal.
- A4 (rev 2): sandwich print, 4 walls, 6/6 shells (1.2 mm skins), 20 % gyroid; about 130 g (solid would be 282 g).
- A5: 7.8 rather than 7.9 so it is never thicker than the glass; tighten the clamp screws a little more.
- A6: PETG for the wet shower area.
- A7: flat shelf face, no drain holes or lip.

## 10. Open questions

- Q1 (answered): bracket layout: one bracket on each wall of the corner.
- Q2 (answered): the 6 in is to the bracket's far edge.
- Q3 (answered): mostly square; only a subtle radius on the front corner: R30 proposed, then R40 (+1 cm, user).
- Q5 (answered): rev 1 100 %; rev 2 sandwich, 20 % gyroid, 6/6 shells, 4 walls.
- Q4 (non-blocking): caliper: how far a bracket sticks out from the wall, and the slot gap inside it (D15).
