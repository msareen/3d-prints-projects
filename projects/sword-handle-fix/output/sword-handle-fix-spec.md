# sword-handle-fix: specification

Status: **confirmed**, revision 1. Units: mm. Quantity: 2 (both on one plate).

## 1. Description

This is a closed-end cap, a new pommel end, for a toy sword. The sword has a green plastic blade and a hollow black handle made of two shells. The handle has broken open at the pommel end, and the cap slides 15 mm over the broken end and is glued on.

As the user asked, the bore is **straight**, sized to the largest handle readings (31.6 wide × 28.3 thick) plus a 0.3 mm glue gap per side. The handle is thinner near the broken edge (19.9 thick there), and gap-filling glue takes up the difference.

The outside is decorative. It bulges outward like a pommel knob, a circular arc that adds 2 mm per side at mid-height (41.0 × 37.7 there, 37.0 × 33.7 at both ends). Three stepped chevron grooves on each wide face point toward the guard, echoing the handle's chevrons. The closed end is 2.4 mm thick with a 3 mm vent hole. The cap prints in PLA with the closed end on the bed and the open rim up, with no supports.

## 2. Inputs

- `input/brief.md`: the user's words.
- `input/2026110609*.jpg` (7 photos): caliper readings on the broken sword. Width 28.8 / 29.1 / 31.6; thickness 19.9, 21.4, 22.6, 24.1, 26.0, 27.7, 28.3; broken zone 15.1; one photo of the whole sword.
- `input/tapper/*.jpg` (5 photos): a second, intact sword on a cm mat, reference only. It has a closed rounded end with a small hole. Readings 23.3 / 28.2 / 30.3 at about 2.5 / 3 / 4 cm from the end.

## 3. Datum and orientation

- Origin: the centre of the bore, on the bed. Z = 0 is the outside of the closed end.
- X: across the handle width (the chevron face).
- Y: across the handle thickness. The front faces -Y.
- Z: up. This is the print direction and points towards the guard.
- Print orientation: closed end on the bed, open rim up. All walls are vertical, so there are no overhangs.

## 4. Dimension register

| ID | Name | Value | Tol | Basis | Conf. | Crit. | Fit | Source |
|---|---|---|---|---|---|---|---|---|
| D1 | handle width, largest reading | 31.6 | ±0.2 | measured | high | yes | free | 093337 '31.6', user confirmed |
| D2 | handle thickness, largest reading | 28.3 | ±0.2 | measured | high | yes | free | 093520 '28.3', user: thickest only |
| D3 | thickness at broken edge (ref.) | 19.9 | | measured | high | | | 093457 '19.9' |
| D4 | cap depth over the handle | 15.0 | ±0.2 | given | high | yes | | brief; 093612 '15.1' |
| D5 | bore corner radius | 8.0 | | estimated | medium | | | 093318 barrel section |
| D6 | side wall at both ends | 2.4 | | default | high | | | 6 perimeters |
| D7 | closed end thickness | 2.4 | | default | high | | | 12 layers |
| D8 | glue gap per side | 0.3 | | default | high | | free | PLA profile |
| D9 | printed bore width | 32.2 | | derived | high | yes | free | D1 + 2·D8 |
| D10 | printed bore thickness | 28.9 | | derived | high | yes | free | D2 + 2·D8 |
| D11 | outer width at both ends | 37.0 | | derived | high | | | D9 + 2·D6 |
| D12 | outer thickness at both ends | 33.7 | | derived | high | | | D10 + 2·D6 |
| D13 | overall height | 17.4 | | derived | high | | | D7 + D4 |
| D14 | vent hole Ø | 3.0 | | default | high | | | glue/air escape |
| D15 | *(deleted: closed-end chamfer, replaced by the bulge)* | | | | | | | |
| D16 | outer chamfer, rim | 0.6 | | default | high | | | |
| D17 | lead-in inside rim | 0.6 | | default | high | | | guides cracked edges in |
| D18 | outward bulge per side, mid-height | 2.0 | | default | high | | | user: "outward bulge"; arc leans ≤ 26° |
| D19 | chevron groove depth | 0.7 | | default | high | | | leaves ≥ 1.7 wall |
| D20 | groove ramp angle (°) | 15 | | default | high | | | keeps undersides < 45° |
| D21 | chevron pitch | 3.5 | | default | high | | | 3 per face |
| D22 | lowest chevron apex Z | 6.0 | | default | high | | | apexes Z 6.0 / 9.5 / 13.0 |
| D23 | chevron arm angle (°) | 25 | | estimated | medium | | | 093346 handle chevrons |
| D24 | outer width at the bulge | 41.0 | | derived | high | | | D11 + 2·D18 |
| D25 | outer thickness at the bulge | 37.7 | | derived | high | | | D12 + 2·D18 |
| D26 | side wall at mid-height | 4.4 | | derived | high | | | D6 + D18 |

## 5. Features

- F1 cap body: a rounded rectangle offset outward from the bore, centred on the origin and 17.4 tall. The offset is 2.4 at Z = 0 and at the rim and 4.4 at Z = 8.7 (a circular arc), with a 0.6 chamfer at the rim.
- F4 chevron grooves: 3 per wide face (±Y), with the apex on X = 0 at Z 6.0 / 9.5 / 13.0 and the arms running down and out at 25°. Each groove has a flat shelf facing up at the bottom (0.7 deep) and a 15° ramp back out above it. The grooves fade out around the corners.
- F2 bore: a straight rounded rectangle 32.2 × 28.9 with corner R8, 15 deep from Z = 2.4 to the rim, with a 0.6 lead-in at the rim.
- F3 vent: Ø3 through the closed end at X = 0, Y = 0.

## 6. Assumptions

- A1: The bore is straight at the largest readings. The gap on the narrow faces can reach about 4.5 mm per side at the broken edge, so use a gap-filling glue (2-part epoxy or hot glue), not thin superglue.
- A2: The R8 rounded rectangle approximates the barrel-shaped section of the handle.
- A3: The cap covers 15 mm of handle and does not restore any length lost at the break.
- A5: The bed is 250 × 210 (Prusa MK4 class).
- A6: The second sword in `input/tapper/` is a reference only.
- A7: The outside is decorative: a 2 mm outward bulge (requested by the user) and stepped chevron grooves. The closed-end chamfer (D15) is dropped because the bulge already rounds the base.

## 7. Consistency checks

- D9 = 31.6 + 2 × 0.3 = 32.2 ✓; D11 = 32.2 + 2 × 2.4 = 37.0 ✓
- D10 = 28.3 + 2 × 0.3 = 28.9 ✓; D12 = 28.9 + 2 × 2.4 = 33.7 ✓
- D13 = 2.4 + 15.0 = 17.4 ✓
- Bulge: D24 = 37.0 + 2 × 2.0 = 41.0 ✓, D25 = 33.7 + 4.0 = 37.7 ✓. Arc radius (8.7² + 2²) / 4 = 19.9, steepest lean asin(8.7 / 19.9) = 26° < 45° ✓
- Chevrons: the top apex 13.0 plus the 2.6 ramp gives 15.6, below the rim chamfer at 16.8 ✓. Groove 0.7 in a wall of 2.4 or more leaves at least 1.7 ✓
- Bore corner R8 < half of 28.9 ✓. Walls 2.4 ≥ 0.8 ✓.

## 8. Open questions

None are blocking. Taper: straight at the thickest (user). End: closed. Material: PLA, 0.4 nozzle.

## Revisions

- Rev 1 (2026-11-06): first issue, confirmed by the user, 2 per plate. Before confirmation, the outside was changed to an outward bulge with chevron grooves at the user's request, and D15 was deleted.
