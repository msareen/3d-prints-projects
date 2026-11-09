# u-hook-adaptor-holder: design specification

> Status: **confirmed**, revision 2. All dimensions in mm. Machine-readable twin:
> `spec.json` (same IDs). The model is built only from what is written here.

Revisions:
- rev 1 (2026-11-09): first spec, brick lying on its 25.6 edge in a long J cradle.
- rev 1, draft b (2026-11-09, before confirmation): the brick now stands vertical (user, after the first render).
  The cup is 58.2 wide instead of 98, the bottom is open for the DC cable and USB-A, and the top is open for the AC input.
  The hook strip is dropped (the pins sit in the back wall). D10 and D11 were deleted, and D33 and D34 were added.
- rev 1, draft c (2026-11-09, before confirmation): the pins are round with no teardrop (user).
  Each pin is 7.6 outer with a 1.7 wide, 5.6 groove against the back face that grips the 1.6 steel (user caliper, D27).
  Supports are now optional, under the pins only.
- rev 1, confirmed (2026-11-09): the user asked for the outputs.
  A pin test sample was added as a second part (F7, D35-D38).
- rev 2 (2026-11-09): the user printed the sample and reported a very good fit. Changes:
  - pin head 7.6 → 9.6 (D19);
  - point-down teardrops back on the groove and the head, for grip and to print without supports;
  - groove kept at 5.6 across and 1.7 wide (the sample proved it). Supports are off again.

## 1. Purpose and context

An upright cup that hangs a Surface 65 W power brick (model 1706, caliper
90.4 x 50.6 x 25.6) on the blue rack upright, using two of its keyhole
slots. The brick stands on its end so it takes only 58 mm of rack width:
- **Top, open:** the AC input, centred.
- **Bottom, open:** the DC output cable and USB-A port, through a full-width opening.

The brick is held by its edges. Walls and back are a large diamond mesh for
cooling. Load: about 0.3 kg plus the cables.

## 2. Inputs reviewed

| File | Kind | What it shows / says | Usable for |
|---|---|---|---|
| input/20261109_150626.jpg | photo | Blue upright with keyhole slots, cm ruler flat on its face. Ruler marks 0 cm 295 px, 4 = 667, 5 = 756, 8 = 1016, 9 = 1100 (86-92 px/cm) | keyhole size and pitch (estimated) |
| input/Frontview.png | sketch | Front view, no numbers: strip with two circles at the left, wider box below | pins at the left end |
| input/41r-UDbVOgL.jpg | photo | Surface 65 W product photo: DC cable and USB-A port on the same short end | port layout |
| input/brief.md + chat | text | J holder, two pins into the big holes then slide down, held from the edges, large mesh. Caliper 50.6 x 25.6, length 90.4. Vertical, AC input on top centred, USB-A beside the output. PLA | D1-D3, layout, material |
| web: B&H, Microsoft 65W Surface Power Supply (W8Y-00001) | text | 89.92 x 50.04 x 24.89 mm, 1x USB-A | cross-check: caliper values are 0.5-0.7 larger, so caliper is used |

Photo transcription (keyholes, full-res px): keyhole 1 top 322, slot end 505,
head width 96-100, slot 57; keyhole 2 top 676, end 845, head 97, slot 55;
keyhole 3 top 1005, end 1162, head 99, slot 57.

## 3. Coordinate system and datum

- Origin: left outer face (X), back face on the rack (Y), frame underside (Z).
- X: left to right seen from the front (brick width 50.6).
- Y: +Y towards the rack. Cup at -Y, pins stick out to +Y.
- Z: up, print direction (brick length 90.4). The part sits on Z = 0, printed as used.
- Front faces -Y.

## 4. Overall description

One piece, a J seen from the side. The **back wall** is 4 mm thick and rises
to Z = 73. The **front and side walls** are 3 mm thick and 30 mm tall above a
3 mm **bottom frame**. The cup inside is 52.2 wide x 27.2 deep (brick + 0.8
per side).

The frame is open across the full inner width between two 5 mm ledges, one
under the brick's front edge and one under its back edge. That leaves an
opening 52.2 x 17.2, so the DC cable and a plugged-in USB-A plug drop
straight down.

The top is open, and the brick stands 20.4 mm above the back wall so its
AC plug is free. Lower the brick in from the top and lift it out.

**Pins:** two on the back face, in a solid 20 mm column at the left end,
centred at X = 10, Z = 27 and Z = 65 (38 mm pitch). Each pin is 4.7 mm
long. Against the back face it has a groove 1.7 mm wide and 5.6 mm across,
then a head 9.6 mm across and 3 mm thick. Both are point-down teardrops,
so the undersides are 45 deg and print without support, and the groove's
point seats in the round bottom of the slot. The slot edges (1.6 mm steel)
are held between the head and the back wall. To hang the holder, push both heads into the round
holes, then let it drop about 10 mm so the grooves ride down the slots.

**Mesh:** 10 mm diamonds on a 14 mm staggered lattice (2.8 mm webs), inside 4 mm
solid borders:
- back wall, right of the pin column: 8 rows;
- front wall: 1 row of 3;
- each side wall: 1 diamond.

No fillets.

**Pin test sample (second part):** the holder's 20 mm pin column on its own.
It is a 4 mm plate, 54 tall, with the same two pins at the same 38 mm
pitch, standing on a 14 x 2 mm foot. It sits 10 mm to the right of the
holder on the plate. Print it first to check the fit.

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source | Model param |
|---|---|---|---|---|---|---|---|---|
| D1 | brick length, vertical (Z) | 90.4 | ±0.1 | measured | high | no | caliper; web 89.92 | BRICK_L |
| D2 | brick thickness (Y) | 25.6 | ±0.1 | measured | high | yes (free) | caliper; web 24.89 | BRICK_D |
| D3 | brick width (X) | 50.6 | ±0.1 | measured | high | yes (free) | caliper; web 50.04 | BRICK_W |
| D4 | extra per-side room (+ free 0.30) | 0.5 | | default | high | no | total 0.8/side | CRADLE_SLACK |
| D5 | back wall thickness | 4.0 | | default | high | no | carries pins | BACK_T |
| D6 | front / side wall thickness | 3.0 | | default | high | no | | WALL_T |
| D7 | bottom frame thickness | 3.0 | | default | high | no | 15 layers | FLOOR_T |
| D8 | back wall height above frame top | 70.0 | | default | high | no | both pins + margin | BACK_H |
| D9 | front / side wall height above frame top | 30.0 | | default | high | no | J front | LIP_H |
| D12 | solid pin column width | 20.0 | | default | high | no | Frontview.png | PIN_COL_W |
| D13 | pin centre X | 10.0 | | derived | high | no | D12 / 2 | PIN_X |
| D14 | lower pin centre Z | 27.0 | | default | high | no | | LOWER_PIN_Z |
| D15 | pin pitch = keyhole pitch | 38.0 | ±1.5 | estimated | medium | no* | photo 37.8 / 38.2 | PIN_PITCH |
| D16 | back wall top above upper pin | 8.0 | | default | high | no | | STRIP_TOP_MARGIN |
| D17 | pin groove width across, teardrop | 5.6 | | measured | high | no* | rev 1 sample fitted (user) | NECK_D |
| D18 | pin groove width | 1.7 | | given | high | no* | user: 1.6 steel + 0.1 | NECK_L |
| D19 | pin head width, teardrop | 9.6 | | given | high | no* | user rev 2: 7.6 + 2 | HEAD_D |
| D20 | pin head thickness | 3.0 | | default | high | no | | HEAD_T |
| D21 | diamond opening | 10.0 | | default | high | no | brief: large mesh | DIAMOND_D |
| D22 | diamond pitch | 14.0 | | default | high | no | 2.8 web | DIAMOND_PITCH |
| D23 | mesh border | 4.0 | | default | high | no | | MESH_BORDER |
| D24 | keyhole round hole Ø (ref) | 11.0 | ±0.8 | estimated | medium | no* | photo | |
| D25 | keyhole slot width (ref) | 6.2 | ±0.5 | estimated | medium | no* | photo | |
| D26 | keyhole length (ref) | 19.5 | ±1 | estimated | medium | no | photo | |
| D27 | upright steel thickness (ref) | 1.6 | ±0.05 | measured | high | no | user caliper | |
| D28 | cup inner width | 52.2 | ±0.3 | derived | high | yes | D3 + 1.6 | |
| D29 | cup inner depth | 27.2 | ±0.3 | derived | high | yes | D2 + 1.6 | |
| D30 | overall width | 58.2 | | derived | high | no | D28 + 2 x D6 | |
| D31 | overall depth without pins | 34.2 | | derived | high | no | D5 + D29 + D6 | |
| D32 | overall height | 73.0 | | derived | high | no | D7 + D8 | |
| D33 | bottom ledge width (Y) | 5.0 | | default | medium | no | edges only | LEDGE_W |
| D34 | bottom opening (Y) x full inner width | 17.2 | ±0.3 | derived | high | yes | D29 - 2 x D33 | |
| D35 | holder-to-sample gap on the plate | 10.0 | | default | high | no | placement | SAMPLE_GAP |
| D36 | sample lower pin centre Z | 8.0 | | default | high | no | head clears bed 4.2 | SAMPLE_PIN_Z |
| D37 | sample foot depth | 14.0 | | default | high | no | stability | FOOT_D |
| D38 | sample foot thickness | 2.0 | | default | high | no | | FOOT_T |

D10 and D11 (end lips, cable slots of the lying layout) are deleted.

\* These sizes set the pin-to-keyhole fit, but the keyhole sizes are scaled
from the photo, as you asked. So the pins are given margins wider than the
measuring error:
- the 9.6 mm head goes into an ~11 mm hole, with about 0.7 mm to spare;
- the head grips 1.7 mm on each side of the ~6.2 mm slot;
- the 5.6 mm groove has 0.3 mm of play on each side.

## 6. Features

| ID | Feature | Count | Position (from datum) | Dimensions | Notes |
|---|---|---|---|---|---|
| F1 | bottom frame with opening | 1 | z 0-3; opening x 3-55.2, y -26.2 to -9 | D7, D33, D34 | brick stands on the ledges |
| F2 | back wall + mesh | 1 | x 0-58.2, y -4-0, z 0-73; field x 24-54.2, z 7-69 | D5, D8, D21-D23 | solid pin column x 0-20 |
| F3 | front wall + mesh | 1 | y -34.2 to -31.2, z 0-33 | D6, D9, D21 | |
| F4 | side wall + mesh | 2 | x 0-3 and 55.2-58.2, z 0-33 | D6, D9, D21 | |
| F7 | pin test sample | 1 | x 68.2-88.2, z 0-54, pins z 8 and 46 | D35-D38 + pin dims | same pins and plate as the holder |
| F6 | grooved teardrop pin | 2 | x 10; z 27 and 65; groove y 0-1.7, head y 1.7-4.7 | D13-D20 | point-down teardrops |

## 7. Consistency checks

- Width: 3 + 52.2 + 3 = 58.2 = D30 ✓; 52.2 - 50.6 = 1.6 = 2 x 0.8 ✓
- Depth: 4 + 27.2 + 3 = 34.2 = D31; + pins 1.7 + 3 = 4.7 → 38.9 (39.0 with the teardrop facets) = envelope Y ✓
- Height: 3 + 70 = 73 = 27 + 38 + 8 = D32 ✓
- Bottom: 5 + 17.2 + 5 = 27.2 = D29 ✓; USB-A plug body (about 16 x 8) and the DC strain relief (about 8) pass through 52.2 x 17.2 ✓
- Brick top 3 + 90.4 = 93.4, 20.4 above the back wall: AC plug free ✓
- Pin in keyhole: head 9.6 < 11 hole (0.7 per side), > 6.2 slot (1.7 per side). The teardrop tip is 6.8 below centre, and where the hole meets the slot (4.5 below centre) the tip is 4.5 wide < 6.2 ✓. Groove 5.6 < 6.2 (0.3 per side); groove 1.7 = 1.6 steel + 0.1 ✓
- Bed: holder 58.2 x 38.9 x 73, plus the sample, gives 88.2 x 38.9 x 73 in 180³ ✓. printcheck: 0 warnings, no overhang > 45 deg, walls ≥ 0.8.

## 8. Print setup

- Printer and settings: 180 x 180 x 180 bed, 0.4 nozzle, 0.2 layer, **PLA**, quantity 1.
- Supports: none. The pins are point-down teardrops.
- Orientation: upright, bottom frame on the bed. Layers run along the pins.
- Fit: free (0.30 per side) + 0.5.

## 9. Assumptions

1. A1: keyhole sizes come from the photo. The rev 1 sample proved the groove (5.6 x 1.7) and the 38 pitch. The 9.6 head needs the round hole to be at least ~9.8: re-print the sample first.
2. A2: the steel is 1.6 mm (caliper), so the 1.7 groove leaves 0.1. If the groove binds, it can open in 0.05 mm steps.
3. A3: the DC cable and USB-A port sit within the middle 17 mm of the bottom face, front to back, so the 5 mm ledges stay clear.
4. A4: the brick goes in and comes out from the top. The AC plug is on top.
5. A5: the pins are at the left end, as drawn. They can be centred or mirrored.
6. A6: PLA softens at about 55 °C and the brick runs at 40-50 °C. Don't cover it.
7. A7: same 180 mm printer as the earlier projects.

## 10. Open questions

| ID | Question | Blocking | Answer |
|---|---|---|---|
| Q1 | Brick length? | yes | 90.4 (caliper) |
| Q2 | Brick orientation? | yes | vertical: AC on top centred, DC + USB-A at the bottom |
| Q3 | Retention? | yes | held by its edges; top and bottom open |
| Q4 | Material? | yes | PLA |
| Q5 | Keyhole sizes source? | no | ruler in the photo |
| Q6 | Pin size with the 1.7 groove? | yes | rev 1: 7.6 outer / 5.6 groove, round |
| Q8 | Rev 2 pin change? | yes | head 9.6, teardrop back, groove kept 5.6 |
