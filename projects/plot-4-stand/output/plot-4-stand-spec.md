# plot-4-stand: design specification

> Status: **confirmed**, revision 2. All dimensions in mm. Machine-readable twin:
> `spec.json` (same IDs). The model is built only from what is written here.

## Revisions

- Rev 1: first spec (tapered channel).
- Rev 2: channel is a clip, not a taper. Lips at the opening (outer side) narrow it to 12.9 (original 12.7) and grip the board rail's 12.8 end (215353, 215633); below them it widens to 15.2 (original 15.0; board rail body 15.0, 215421). Lip depth 3.0 is estimated (D25, Q6); 45° lip underside, 0.5 lead-in (D26). User: "it is outer side to catch, think how it will clip on".

## 1. Purpose and context

A printable copy of a blue spare foot (input/brief.md: "this is the spare
part") for an upright perforated game board. The board's edge rail slides into
the foot's handle channel. In use (input/20261105_215633.jpg) the foot stands
on the end faces of its two arms, with the half ring vertical and the handle
pointing up. The board's vertical side rail drops into the channel, the panel
leaves through the channel's open side, and the board's bottom corner rests on
the outer ring wall. The channel is the only mating feature; the ring only
gives the footprint.

## 2. Inputs reviewed

| File | Kind | What it shows / says | Usable for |
|---|---|---|---|
| input/brief.md | text | user's words: copy the spare part; PLA; Bambu/Prusa 0.4 | goal, print setup |
| input/20261105_213638.jpg | photo | open side up on a cm mat, about 99 px/cm | D1, D17 (estimated), D4 check, outline |
| input/20261105_213652.jpg | photo | floor side up: flat bottom, handle flush | floor plane |
| input/20261105_213709.jpg | photo | open side up, closer; taper line in the handle channel | outline, A3 |
| input/20261105_213755.jpg | photo | caliper across the handle: "20.6 mm" | D10 |
| input/20261105_213829.jpg | photo | caliper across one arm end: "20.4 mm" | D2 |
| input/20261105_213910.jpg | photo | caliper over the handle end: "9.6 mm"; handle end open | D15 |
| input/20261105_213947.jpg | photo | caliper inside the channel at the floor: "12.7 mm" | D11 |
| input/20261105_214036.jpg | photo | caliper inside the channel at the top: "15.0 mm" | D12 |
| input/20261105_214111.jpg | photo | caliper on a handle wall, part way down: "3.3 mm" | A3 check |
| input/20261105_214128.jpg, 214133.jpg | photo | caliper on a handle wall at the top: "2.6 mm" | D13 cross-check |
| input/20261105_214151.jpg | photo | caliper on the other handle wall at the top: "2.8 mm" | D13 |
| input/20261105_214205.jpg | photo | caliper on a handle wall at the base: "4.0 mm" | D14 |
| input/20261105_215353.jpg | photo | the board the foot fits; caliper across its edge rail at the end: "12.8 mm" | D20 |
| input/20261105_215421.jpg | photo | caliper across the board's edge rail further in: "15.0 mm" | D21 |
| input/20261105_215633.jpg | photo | the foot in use: on its arm ends, board rail in the handle channel | orientation in use, A9 |

## 3. Coordinate system and datum

- Origin: centre of the arcs, on the plane of the arm-end faces, Z = 0 on the underside of the floor.
- X: across the U, left arm to right arm seen from the front.
- Y: from the arm ends towards the arc apex and handle.
- Z: up, print direction; floor on the bed, open side up.
- Front of the part faces -Y: the front elevation looks at the two arm ends.

## 4. Overall description

A shallow open tray shaped as a half ring. Outer and inner arcs are concentric
half circles, R47.7 and R27.3, centred on the origin and spanning Y ≥ 0. The
ring is 20.4 wide. The tray has a flat floor, an outer and an inner curved
wall, and a closed end wall at each arm end, flush with Y = 0. The rim stands
about 10 high, with a flat top.

A straight handle sits on the symmetry axis (X = 0) and runs from the outer
arc out to Y = 69.5. It is a U-channel, 20.6 wide outside and 9.6 high, with
its floor flush with the tray floor. It is open at the top and at its outer
end, and closed at its inner end by the tray's outer wall. The inner faces of
it is a clip. Lips along the top of both side walls narrow the opening to
12.9 (12.7 on the original) and grip the narrow 12.8 end of the board's side
rail. Below the lips the channel widens to 15.2 (15.0 on the original) down
to the floor. Each lip is 1.15 wide, with a vertical catch face 3.0 deep
(estimated), a 45° underside back to the 2.7 wall (so no support is needed),
and a 0.5 lead-in on top so the rail pushes in.

The bottom outer edges have a 0.4 chamfer. Ejector marks are not copied. The
part is symmetric about X = 0.

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source | Model param |
|---|---|---|---|---|---|---|---|---|
| D1 | outer width across the U | 95.4 | ±1.5 | estimated | medium | no | mat scale 213638. **Q2** | |
| D2 | ring band width at the arm ends | 20.4 | ±0.2 | measured | high | no | 213829 "20.4" | |
| D3 | outer arc radius | 47.7 | | derived | medium | no | D1 / 2 | |
| D4 | inner arc radius | 27.3 | | derived | medium | no | D3 - D2 (photo 26.6) | |
| D5 | ring wall height overall | 10.0 | | estimated | low | no | not measured. **Q3** | |
| D6 | floor thickness | 1.6 | | estimated | low | no | **Q4** | |
| D7 | outer curved wall thickness | 1.8 | | estimated | low | no | **Q4** | |
| D8 | inner curved wall thickness | 1.5 | | estimated | low | no | **Q4** | |
| D9 | arm end wall thickness | 1.5 | | estimated | low | no | **Q4** | |
| D10 | handle outer width | 20.6 | ±0.2 | measured | high | no | 213755 "20.6" | |
| D11 | original opening between the lips (ref) | 12.7 | ±0.2 | measured | high | no | 213947 "12.7" | |
| D12 | original width below the lips (ref) | 15.0 | ±0.2 | measured | high | no | 214036 "15.0" | |
| D13 | handle side wall below the lips | 2.8 | ±0.2 | measured | high | no | 214151 "2.8" (other wall "2.6") | |
| D14 | side wall + lip at the opening (ref) | 4.0 | ±0.2 | measured | high | no | 214205 "4.0" | |
| D15 | handle height | 9.6 | ±0.2 | measured | high | yes | 213910 "9.6" | |
| D16 | handle floor thickness | 2.0 | | estimated | low | no | **Q4** | |
| D17 | overall length, arm ends to handle end | 69.5 | ±1.5 | estimated | medium | no | mat scale 213638. **Q2** | |
| D18 | handle length beyond the arc apex | 21.8 | | derived | medium | no | D17 - D3 | |
| D19 | bottom elephant-foot chamfer | 0.4 | | default | high | no | design rules | |
| D20 | board rail narrow end (in the lips) | 12.8 | ±0.1 | measured | high | yes (press) | 215353 "12.8" | |
| D21 | board rail body above the step | 15.0 | ±0.1 | measured | high | yes (snug) | 215421 "15.0" | |
| D22 | printed opening between the lips | 12.9 | | derived | high | yes (press) | D20 + 2 x 0.05 (PLA press) | |
| D23 | printed width below the lips | 15.2 | | derived | high | yes | D21 + 2 x 0.10 (PLA snug) | |
| D24 | printed lip width / side wall | 1.15 / 2.7 | | derived | high | no | (D23 - D22) / 2, (D10 - D23) / 2 | |
| D25 | lip depth (vertical catch face) | 3.0 | | estimated | low | no | not measured. **Q6** | EDGE_H |
| D26 | lip lead-in chamfer | 0.5 | | default | high | no | design choice | LEAD_IN |

## 6. Features

| ID | Feature | Count | Position (from datum) | Dimensions | Notes |
|---|---|---|---|---|---|
| F1 | half-ring tray | 1 | arcs centred at X = 0, Y = 0, Y ≥ 0; arm ends on Y = 0 | D1–D9 | floor, 2 curved walls, 2 end walls, open top |
| F2 | U-channel handle | 1 | X = 0, Y = D3 to D17, floor on Z = 0 | D10, D15–D18, D20–D24 | open top and outer end; clip: lips at the opening, wider below; the board rail's narrow end clips in from the top |
| F3 | bottom chamfer | 1 | outer bottom edges | D19 | |

## 7. Consistency checks

- Handle: (D10 - D12) / 2 = (20.6 - 15.0) / 2 = 2.8 = D13 ✓. The lip is (D12 - D11) / 2 = 1.15, and wall + lip = 3.95 ≈ D14 4.0 ✓. Lip 3.0 + 45° underside 1.15 = 4.15 < channel depth 9.6 - 2.0 = 7.6 ✓.
- Board: the rail end 12.8 vs the original's lip opening 12.7 → 0.1 interference, which is the catch. The print's 12.9 comes out about 12.7 on FDM ✓.
- Board vs original channel: rail 12.8 / 15.0 against the channel's 12.7 / 15.0. The moulded original grips with about 0.1 interference at the floor; the print uses snug 0.10 per side, because FDM channels come out about 0.1 per side narrow ✓.
- Ring: D3 - D2 = 27.3. The photo inner opening gives 26.6 → 0.7 apart, inside the photo error. A caliper D1 (Q2) settles it.
- Photo scale: the handle width from the photo, 210 px / 99 / 1.025 = 20.7, against the caliper's 20.6 ✓. This confirms the 2.5 % rim correction used for D1 and D17.
- Heights: the handle (9.6) and the rim (about 10, unmeasured) look level in the side photos. Q3.
- Printability: the thinnest wall is 1.5 (≥ 0.8) ✓; the tapered channel walls lean outward going up, so there is no overhang ✓; the part fits on a 250 x 210 bed ✓.

## 8. Print setup

Bambu / Prusa class printer (bed taken as 250 x 210 x 220), 0.4 nozzle, 0.2
layer, PLA. Floor on the bed, open side up, no supports. Quantity 1 (Q5).
Channel fit: PLA snug, 0.10 per side. If the board is loose or tight, change it
in 0.05 steps.

## 9. Assumptions

1. A1: the arcs are concentric half circles centred on the arm-end plane.
2. A2: the floor ejector marks and dots are not copied.
3. A3: the channel is a clip. Lips at the opening grip the board rail's 12.8 end; below them it widens to 15.2.
4. A4: the rim top is flat, with no lips or fillets.
5. A5: bed 250 x 210 (Prusa class); every Bambu bed is larger.
6. A6: lips use PLA press (0.05 per side), the wide part PLA snug (0.10). PLA is stiffer than the original: if the clip is too hard to push on or cracks, open the lips in 0.05 steps, or print in PETG.
7. A7: quantity 1 replacement foot.
9. A9: in use the arm-end faces (Y = 0) are the feet: flat and in one plane.
8. A8: ring sizes and wall thicknesses only set the footprint and look; photo estimates are acceptable.

## 10. Open questions

| ID | Question | Blocking | Answer |
|---|---|---|---|
| Q1 | What does the part mate with? | yes | the game board's edge rail, 12.8 / 15.0 (215353, 215421) |
| Q2 | Caliper: outer width across the U (D1), and overall length from the arm ends to the handle end (D17). | no (estimates used) | |
| Q3 | Caliper: overall rim height, part lying floor-down (D5). | no (estimate 10.0 used) | |
| Q4 | Caliper: floor, outer wall, inner wall, arm end wall and handle floor thicknesses. | no (estimates used) | |
| Q5 | Print 1 foot or 2? | no (1) | |
| Q6 | Lip depth: how far down from the handle top the narrow opening goes (D25). | no (3.0 used) | |
