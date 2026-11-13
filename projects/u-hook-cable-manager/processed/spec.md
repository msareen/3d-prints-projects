# u-hook-cable-manager: design specification

> Status: **confirmed**, revision 4. All dimensions in mm. Machine-readable twin: `spec.json` (same IDs).

Revisions:
- rev 1 (2026-11-13): drafted from elevation v3; reworked to elevation v5 (U strap lids, cable space = reference + 2 mm); confirmed (user: look good).
- rev 2 (2026-11-13): loop width 40 overall (user); cable space 35.2 wide.
- rev 3 (2026-11-13): separate lids on a capped pin (so they could be fitted). Released, then rejected by the user: hinge too tight to fit separately.
- rev 4 (2026-11-14): print in place like the reference (user): the whole part prints on its back, lids closed on 3-knuckle hinges (tongue on the base, 45 deg cone pins), legs 0.3 above 5 mm posts, skirt-and-barb latch. Deleted: D16 (base strip; the loop base is now the 4 mm plate ear), D20-D23 (pin, ring, cap, slit), D30 (lid spacing). Added D33-D37. D24-D27 and D32 changed.

## 1. Purpose and context

A cable manager for the same rack keyholes as the adaptor holder. A 20 x 54 x 4 plate carries the two teardrop rack pins (z 8 and 46) and, centred on each pin, a cable loop 40 wide and 12 long: a rounded U strap lid (2.4 wall, R6 outside) over a 35.2 x 12 cable space, hinged along the cable on a 3-knuckle hinge with 45 deg cone pins and closed by a skirt-and-barb latch, like the reference Deskcable organiser. Everything prints in place in one go, lying on its back (rack pin heads on the bed, lids on top, already on their hinges); the only support is under the plate's back. A 12 x 20 window saves material. PLA, one per plate.

## 2. Inputs reviewed

| File | Kind | Notes |
|---|---|---|
| input/brief.md | text | the user's words |
| input/elevation.svg | sketch | assistant-drawn elevation v6 (loop 40 wide), approved by the user; the hinge detail is superseded by rev 4 |
| projects/u-hook-adaptor-holder/processed/spec.json | text | plate, rack pins, keyhole sizes |
| ~/Downloads/Deskcable_organiser.3mf (not in the repo) | model | reference; sections measured: base 4, cavity 31.75 x 10, walls 4-5, outer R ~8, 3-knuckle print-in-place hinge (tongue on the base, ~2.5 pins), lid legs 0.25-0.3 above the posts |

## 3. Coordinate system and datum

- Origin: design frame: left face of the plate (X), back face (Y), plate bottom end (Z); the model files are in print orientation: print X = X, print Y = Z, print Z = 4.75 - Y
- X: left to right seen from the front
- Y: towards the rack: +Y = back; loops at -Y, rack pins at +Y
- Z: along the cable (up in use); print Z = up from the bed, the rack pin heads sit on Z = 0
- Front (the lids) faces -Y in the design frame, +Z (up) when printed.

## 4. Overall description

One print-in-place part with three bodies. **Plate:** 20 x 54 x 4 with the two grooved teardrop rack pins on its back (x 10, z 8 and 46) and a 12 x 20 window between the loops. **Loop bases:** centred on each pin, the plate widens to 40 (x -10 to 30) over 12 mm (z 2-14 and 40-52). On it stand a hinge tongue at the left (3.6 wide, 5 tall, 4.4 long, rounded below the axis, with a 45 deg cone pin 2.4 x 1.2 on each end face; axis x -8.2, y -6.5, along the cable) and a 2.4 x 5 latch post at the right with a notch for the barb.

**Lids (2):** each a rounded U strap, wall 2.4, outer R6, inner R3.6, closing a 35.2 x 12 cable space. Its left leg ends in two 3.5 mm knuckles, one each side of the tongue (0.3 axial gap), with cone sockets 0.3 clear of the pins and rounded about the axis so they swing clear of the base. The legs stop 0.3 above the posts; the right leg's 1.3 mm skirt runs down outside the latch post to 0.3 above the base, and its 0.5 mm barb (45 deg lead-in) clicks into the post notch. Printed closed, on its back: the rack pin heads touch the bed, support (build plate only) fills the 4.75 mm under the plate, and the lids print on top of the bases like the reference.

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source |
|---|---|---|---|---|---|---|---|
| D1 | plate width (X) | 20.0 |  | derived | high | no | u-hook-adaptor-holder spec D12, pin column width |
| D2 | plate and loop base thickness (Y) | 4.0 |  | derived | high | no | u-hook-adaptor-holder spec D5; reference base 4 |
| D3 | plate length (Z, along the cable) | 54.0 |  | derived | high | no | u-hook-adaptor-holder spec pin test sample height |
| D4 | rack pin pitch | 38.0 | ±1.5 | derived | medium | no | u-hook-adaptor-holder spec D15; proven by the pin sample |
| D5 | lower rack pin centre Z | 8.0 |  | derived | high | no | u-hook-adaptor-holder spec D36 |
| D6 | upper rack pin centre Z | 46.0 |  | derived | high | no | D5 + D4 |
| D7 | rack pin centre X | 10.0 |  | derived | high | no | D1 / 2 |
| D8 | pin groove width across (teardrop) | 5.6 |  | derived | high | no | u-hook-adaptor-holder spec D17 |
| D9 | pin groove width (Y) | 1.7 |  | derived | high | no | u-hook-adaptor-holder spec D18 |
| D10 | pin head width (teardrop) | 9.6 |  | derived | high | no | u-hook-adaptor-holder spec D19 |
| D11 | pin head thickness (Y) | 3.0 |  | derived | high | no | u-hook-adaptor-holder spec D20 |
| D12 | loop length along the cable (Z), centred on its pin | 12.0 |  | default | medium | no | elevation v5 |
| D13 | cable space width (X) | 35.2 |  | derived | high | yes | user rev 2: loop 40 overall; 40 - 2 x D15 |
| D14 | cable space depth (Y), base face to lid | 12.0 |  | given | high | yes | user: reference + 2 mm; reference Deskcable_organiser.3mf (measured sections): 10 |
| D15 | lid wall | 2.4 |  | default | medium | no | user: thinner than the reference (4-5); 6 lines of 0.4 |
| D17 | lid outer corner radius | 6.0 |  | default | medium | no | user: rounder; reference Deskcable_organiser.3mf (measured sections): ~8 |
| D18 | lid inner corner radius | 3.6 |  | derived | high | no | D17 - D15 |
| D19 | clearance between moving faces (hinge, posts, latch) | 0.3 |  | default | medium | no | reference Deskcable_organiser.3mf (measured sections): 0.25-0.3; print-in-place |
| D24 | latch post width (X) | 2.4 |  | default | medium | no | rev 4 |
| D25 | hinge and latch post height above the base (Y) | 5.0 |  | default | medium | no | reference Deskcable_organiser.3mf (measured sections): posts 4; rev 4: 5 so the knuckle can turn |
| D26 | lid latch skirt thickness (X) | 1.3 |  | default | low | no | reference Deskcable_organiser.3mf (measured sections): ~1.25; flexes over the post |
| D27 | latch barb depth (X), 45 deg lead-in | 0.5 |  | default | low | no | rides 0.2 over the post (D27 - D19); test print |
| D28 | window width (X) | 12.0 |  | default | medium | no | user: save material |
| D29 | window length (Z) | 20.0 |  | default | medium | no | 3 mm from each loop |
| D31 | loop width overall (X) | 40.0 |  | given | high | no | user rev 2; centred on the plate |
| D32 | loop depth from the back face (Y) | 18.4 |  | derived | high | no | D2 + D14 + D15 |
| D33 | hinge cone pin base diameter | 2.4 |  | default | medium | no | reference Deskcable_organiser.3mf (measured sections): pins ~2.5; 45 deg cones print without support |
| D34 | hinge cone pin length | 1.2 |  | default | medium | no | 45 deg cone |
| D35 | lid knuckle length (Z), one at each end of the loop | 3.5 |  | default | medium | no | reference Deskcable_organiser.3mf (measured sections): 3-knuckle hinge |
| D36 | hinge tongue length (Z) | 4.4 |  | derived | high | no | D12 - 2 x (D35 + D19) |
| D37 | hinge post / knuckle width (X) | 3.6 |  | default | medium | no | carries the cone pins and sockets |

Deleted IDs: D16, D20, D21, D22, D23, D30 (see rev 4).

## 6. Features

| ID | Feature | Count | Position | Dims | Notes |
|---|---|---|---|---|---|
| F1 | back plate with window | 1 | x 0-20, y -4-0, z 0-54; window x 4-16, z 17-37 | D1, D2, D3, D28, D29 | printed lying on its back: the window is a vertical hole |
| F2 | rack pin (grooved teardrop) | 2 | x 10; z 8 and 46; +Y | D4, D5, D6, D7, D8, D9, D10, D11 | the pin heads are the bed contact; support under the plate's back |
| F3 | loop base: 40 mm wide base, hinge tongue with two cone pins, latch post with notch | 2 | x -10 to 30, y 0 to -9, z 2-14 and 40-52 | D2, D12, D25, D24, D33, D34, D36, D37 | hinge axis x -8.2, y -6.5, along Z |
| F4 | lid: rounded U strap with two knuckles and a latch skirt | 2 | x -10 to 30, y -4.3 to -18.4, same z as F3; printed in place, closed | D13, D14, D15, D17, D18, D19, D26, D27, D35 | legs rest 0.3 above the posts and base; opens about 105 deg |

## 7. Consistency checks

- Loop width: 35.2 + 2 x 2.4 = 40 = D31, centred on x 10 (x -10 to 30)
- Loop depth: 4 + 12 + 2.4 = 18.4 = D32; print height 4.75 + 18.4 = 23.15 = envelope Z
- Hinge along the loop: 3.5 + 0.3 + 4.4 + 0.3 + 3.5 = 12 = D12
- Hinge axis 2.5 below the base face: knuckles rounded to 2.2 about it (0.3 clear of the base); tongue rounded to 2.2 below it; lid cleared to 3.38 round it in the tongue zone
- Pins: 8 + 38 = 46; loops 8 +/- 6 and 46 +/- 6; plate 54; window z 17-37, 3 mm from each loop
- Motion (manifold3d sweep, both loops): closed 0 overlap; 0-4 deg the barb rides 0.2 over the post (the click); 6-105 deg free; the lid stops on the base at about 110 deg; the cone pins never touch their sockets
- printcheck: pass; print in place: both lids rest 0.30 above the base (checked on every lowest face); warnings: overhang (the plate's back over support, the lid ceilings bridge about 28 mm like the reference), thin barb tip, levels off the 0.2 grid
- Bed: 40 x 54 x 23.15 in 180 x 180

## 8. Print setup

- Printer and settings: 180 x 180 x 180 bed, 0.4 nozzle, 0.2 layer, **PLA**, quantity **1 per plate**.
- Supports: **on build plate only** (fills the 4.75 mm under the plate's back; none in the hinges or the cable spaces).
- Orientation: on its back: rack pin heads on the bed, plate and loop bases above them, lids on top, printed closed on their hinges; supports on build plate only (under the plate's back, 4.75 mm).

## 9. Assumptions

- A1: one loop centred on each rack pin (user).
- A2: loop 40 wide (user); cable space depth = reference + 2 mm (user).
- A3: print in place on its back, like the reference (user, rev 4): the lids print on their hinges; only the plate's back needs support (build plate only).
- A4: gaps (D19), barb (D27) and skirt (D26) are first guesses for PLA, checked by the motion sweep only; print one and adjust in 0.05 mm steps.
- A5: the rack pins now print with their layers across them (they stood upright in the tested sample); fine for the light load of cables.
- A6: the lid ceiling bridges about 28 mm over the cable space, as in the reference.

## 10. Open questions

| ID | Question | Blocking | Answer |
|---|---|---|---|
| Q1 | Cable size? | yes | reference cavity + 2 mm (user) |
| Q2 | Each loop centred on its pin? | yes | yes (user) |
| Q3 | Quantity per plate? | no | one per plate (user) |
| Q4 | Loop width? | yes | 40 mm overall (user, rev 2) |
| Q5 | Separate lids or print in place, and orientation? | yes | print in place, on its back with support under the plate (user, rev 4) |
