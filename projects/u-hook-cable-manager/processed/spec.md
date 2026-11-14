# u-hook-cable-manager: design specification

> Status: **confirmed**, revision 9. All dimensions in mm. Machine-readable twin: `spec.json` (same IDs).

Revisions:
- rev 1 (2026-11-13): drafted from elevation v3; reworked to elevation v5 (U strap lids, cable space = reference + 2 mm); confirmed (user: look good).
- rev 2 (2026-11-13): loop width 40 overall (user); cable space 35.2 wide.
- rev 3 (2026-11-13): separate lids on a capped pin (so they could be fitted). Released, then rejected by the user: hinge too tight to fit separately.
- rev 4 (2026-11-14): print in place like the reference (user): the whole part prints on its back, lids closed on 3-knuckle hinges (tongue on the base, 45 deg cone pins), legs 0.3 above 5 mm posts, skirt-and-barb latch. Deleted: D16 (base strip; the loop base is now the 4 mm plate ear), D20-D23 (pin, ring, cap, slit), D30 (lid spacing). Added D33-D37. D24-D27 and D32 changed. Printed by the user: support under the back too much material, latch too loose.
- rev 5 (2026-11-14): upright again with no support (user); lids print flat and drop onto a plain 4 mm vertical pin (no tight fit); latch barb 0.50 -> 0.55 (+0.05, user: too loose) in a closed pocket so a closed lid cannot lift off. Deleted D33-D37 (cone hinge); added D38-D42.
- rev 6 (2026-11-14): user: the drop-on lids broke while fitting; print in place again, upright (support only under the upper lid), loop 2 mm taller (14) and a bigger, tighter hinge: 3-knuckle, tongue 4.4 x 6 on the base, 3.0 x 1.4 cone pins, 0.25 cone clearance, 0.4 axial gaps. Lower loop on the bed: pins z 7 and 45, plate 53. Deleted D38-D42; added D43-D49; D3, D5, D6, D12, D25, D29 changed.
- rev 7 (2026-11-14): latch after seba-med-cap (user): a 45/45 bead (0.7) on the latch post and a 45/45 hook on a 1.0 skirt arm, printed 0.3 apart; the hook flexes 0.4 over the bead (seba PLA depth). Deleted D27 (barb); added D50, D51; D26 1.3 -> 1.0.
- rev 8 (2026-11-14): latch bead 0.70 -> 0.75 (user: raise it); hook travel 0.45, arm strain 2.4 %.
- rev 9 (2026-11-14): latch bead 0.75 -> 1.05 (user: snapping still not good, tighter by 0.3 mm, not a 0.05 step). Hook travel 0.75; the 1.0 mm arm now bends to about 4.6 % strain, above the usual ~3 % PLA guide: watch for cracking or a set.

## 1. Purpose and context

A cable manager for the same rack keyholes as the adaptor holder. A 20 x 53 x 4 plate carries the two teardrop rack pins (z 7 and 45) and, centred on each pin, a cable loop 40 wide and 14 tall: a rounded U strap lid (2.4 wall, R6 outside) over a 35.2 x 12 cable space, hinged along the cable on a 3-knuckle hinge with 45 deg cone pins (printed in place, like the reference) and closed by a bead-and-hook click latch taken from seba-med-cap. Printed upright as used: the lower loop stands on the bed, the upper lid needs support under it only. A 12 x 18 window saves material. PLA, one per plate.

## 2. Inputs reviewed

| File | Kind | Notes |
|---|---|---|
| input/brief.md | text | the user's words |
| input/elevation.svg | sketch | assistant-drawn elevation v6 (loop 40 wide), approved by the user; the hinge detail is superseded by rev 6 |
| projects/u-hook-adaptor-holder/processed/spec.json | text | plate, rack pins, keyhole sizes |
| ~/Downloads/Deskcable_organiser.3mf (not in the repo) | model | reference; sections measured: base 4, cavity 31.75 x 10, walls 4-5, outer R ~8, 3-knuckle print-in-place hinge (tongue on the base, ~2.5 pins), lid legs 0.25-0.3 above the posts |

## 3. Coordinate system and datum

- Origin: left face of the plate (X), back face resting on the rack upright (Y), underside of the plate (Z)
- X: left to right seen from the front
- Y: towards the rack: +Y = back; loops at -Y, rack pins at +Y
- Z: up = print direction; printed upright as used, lids closed on their hinges
- Front (the lids) faces -Y in the design frame, +Z (up) when printed.

## 4. Overall description

One print-in-place part (three bodies), printed upright as used. **Plate:** 20 x 53 x 4 with the two grooved teardrop rack pins on its back (x 10, z 7 and 45) and a 12 x 18 window between the loops (round bottom, 45 deg pointed top). **Loop bases:** centred on each pin the plate widens to 40 (x -10 to 30) over 14 mm (z 0-14 on the bed, and 38-52 on 45 deg wings). On it stand a hinge tongue at the left (4.4 wide, 6 deep, 5.2 tall, rounded in front of the axis, with a 45 deg cone pin 3.0 x 1.4 on its top and bottom; vertical axis x -7.8, y -7) and a 2.4 x 6 latch post at the right with a 1.05 mm 45/45 bead on its outer face (the seba-med-cap latch bead).

**Lids (2):** each a rounded U strap, wall 2.4, outer R6, inner R3.6, closing a 35.2 x 12 cable space. Its left leg ends in two 4 mm knuckles, below and above the tongue (0.4 axial gaps), with cone sockets 0.25 clear of the pins, rounded about the axis so they swing clear of the base. The legs stop 0.3 in front of the tongue and post; the right leg's 1.0 mm skirt is the latch arm: it runs back outside the post and its 45/45 hook sits behind the bead, 0.3 clear; opening or closing, the hook flexes 0.75 over the bead (the click). The lower lid stands on the bed; the upper lid is captured on its hinge and needs slicer support under it (it stands on the lower lid).

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source |
|---|---|---|---|---|---|---|---|
| D1 | plate width (X) | 20.0 |  | derived | high | no | u-hook-adaptor-holder spec D12, pin column width |
| D2 | plate and loop base thickness (Y) | 4.0 |  | derived | high | no | u-hook-adaptor-holder spec D5; reference base 4 |
| D3 | plate height (Z) | 53.0 |  | derived | high | no | rev 6: lower loop on the bed; upper pin + 8 (u-hook-adaptor-holder spec D16) |
| D4 | rack pin pitch | 38.0 | ±1.5 | derived | medium | no | u-hook-adaptor-holder spec D15; proven by the pin sample |
| D5 | lower rack pin centre Z | 7.0 |  | derived | high | no | rev 6: D12 / 2, so the lower loop sits on the bed |
| D6 | upper rack pin centre Z | 45.0 |  | derived | high | no | D5 + D4 |
| D7 | rack pin centre X | 10.0 |  | derived | high | no | D1 / 2 |
| D8 | pin groove width across (teardrop) | 5.6 |  | derived | high | no | u-hook-adaptor-holder spec D17 |
| D9 | pin groove width (Y) | 1.7 |  | derived | high | no | u-hook-adaptor-holder spec D18 |
| D10 | pin head width (teardrop) | 9.6 |  | derived | high | no | u-hook-adaptor-holder spec D19 |
| D11 | pin head thickness (Y) | 3.0 |  | derived | high | no | u-hook-adaptor-holder spec D20 |
| D12 | loop height along the cable (Z), centred on its pin | 14.0 |  | given | high | no | user rev 6: 12 + 2 for a bigger hinge |
| D13 | cable space width (X) | 35.2 |  | derived | high | yes | user rev 2: loop 40 overall; 40 - 2 x D15 |
| D14 | cable space depth (Y), base face to lid | 12.0 |  | given | high | yes | user: reference + 2 mm; reference Deskcable_organiser.3mf (measured sections): 10 |
| D15 | lid wall | 2.4 |  | default | medium | no | user: thinner than the reference (4-5); 6 lines of 0.4 |
| D17 | lid outer corner radius | 6.0 |  | default | medium | no | user: rounder; reference Deskcable_organiser.3mf (measured sections): ~8 |
| D18 | lid inner corner radius | 3.6 |  | derived | high | no | D17 - D15 |
| D19 | side clearance between moving faces (legs, posts, latch, knuckles) | 0.3 |  | default | medium | no | reference Deskcable_organiser.3mf (measured sections): 0.25-0.3 |
| D24 | latch post width (X) | 2.4 |  | default | medium | no | rev 4 |
| D25 | hinge tongue and latch post height above the base (Y) | 6.0 |  | default | medium | no | reference Deskcable_organiser.3mf (measured sections): posts 4; rev 6: 6 for the bigger hinge |
| D26 | lid skirt = latch arm thickness (X) | 1.0 |  | derived | medium | no | rev 7: seba-med-cap latch arm D40; strain 3 x 1.0 x 0.45 / (2 x 5.3^2) = 2.4 % |
| D28 | window width (X) | 12.0 |  | default | medium | no | user: save material |
| D29 | window length (Z), round bottom, 45 deg pointed top | 18.0 |  | default | medium | no | rev 6: 3 mm from each 14 mm loop |
| D31 | loop width overall (X) | 40.0 |  | given | high | no | user rev 2; centred on the plate |
| D32 | loop depth from the back face (Y) | 18.4 |  | derived | high | no | D2 + D14 + D15 |
| D50 | latch bead height on the post, 45 deg both faces | 1.05 |  | given | high | no | rev 9: 0.75 + 0.30 (user: snap still not good, tighter by 0.3); rev 7 after seba-med-cap |
| D51 | latch hook travel over the bead (X) | 0.75 |  | derived | high | no | D50 - D19; arm strain 3 x 1.0 x 0.75 / (2 x 4.95^2) = 4.6 %, above the ~3 % PLA guide (user asked for it) |
| D43 | hinge cone pin base diameter | 3.0 |  | default | medium | no | rev 6: bigger hinge (user); reference Deskcable_organiser.3mf (measured sections): pins ~2.5 |
| D44 | hinge cone pin length (45 deg) | 1.4 |  | default | medium | no | rev 6 |
| D45 | lid knuckle height (Z), one below and one above the tongue | 4.0 |  | default | medium | no | rev 6: 3-knuckle hinge like the reference |
| D46 | hinge tongue height (Z) | 5.2 |  | derived | high | no | D12 - 2 x (D45 + D48) |
| D47 | hinge tongue / knuckle width (X) | 4.4 |  | default | medium | no | rev 6: bigger hinge (user) |
| D48 | axial gap tongue / knuckle | 0.4 |  | default | medium | no | two 0.2 layers so it prints open upright |
| D49 | cone pin to socket clearance, normal to the cone | 0.25 |  | default | medium | no | rev 6: tighter hinge (user), 0.30 - 0.05 |

Deleted IDs: D16, D20-D23, D30 (rev 4), D33-D37 (rev 5), D38-D42 (rev 6).

## 6. Features

| ID | Feature | Count | Position | Dims | Notes |
|---|---|---|---|---|---|
| F1 | back plate with window | 1 | x 0-20, y -4-0, z 0-53; window x 4-16, z 17-35 | D1, D2, D3, D28, D29 | window has a 45 deg pointed top so it prints upright |
| F2 | rack pin (grooved teardrop) | 2 | x 10; z 7 and 45; +Y | D4, D5, D6, D7, D8, D9, D10, D11 | same as the adaptor holder, printed upright like the tested sample |
| F3 | loop base: 40 mm ear, hinge tongue with two cone pins, latch post with a 45/45 bead | 2 | x -10 to 30, y 0 to -10, z 0-14 and 38-52 | D2, D12, D24, D25, D43, D44, D46, D47, D50 | hinge axis x -7.8, y -7 (vertical); 45 deg wings under the upper loop beside the plate |
| F4 | lid: rounded U strap with two knuckles and a latch arm with a 45/45 hook | 2 | x -10 to 30, y -4.3 to -18.4, same z as F3; printed in place, closed | D13, D14, D15, D17, D18, D19, D26, D45, D48, D49, D51 | lower lid on the bed; upper lid needs support under it; opens about 105 deg; 45/45 hook clicks past the post bead |

## 7. Consistency checks

- Loop width: 35.2 + 2 x 2.4 = 40 = D31, centred on x 10 (x -10 to 30); depth 4 + 12 + 2.4 = 18.4 = D32
- Hinge along the loop: 4.0 + 0.4 + 5.2 + 0.4 + 4.0 = 14 = D12, all on the 0.2 layer grid
- Hinge axis 3 in front of the base face: knuckles rounded to 2.7 about it; tongue rounded to 2.7 in front of it; lid cleared to 4.02 round it beside the tongue; cone socket 1.45 at the knuckle face, wall 1.25
- Pins 7 + 38 = 45; loops 7 +/- 7 = 0-14 and 45 +/- 7 = 38-52; plate 53 = 45 + 8; window z 17-35, 3 mm from each loop
- Latch: hook apex 0.3 off the post, bead 1.05 high: travel 0.75; arm strain 3 x 1.0 x 0.75 / (2 x 4.95^2) = 4.6 % (above the ~3 % PLA guide, user request); 45 deg faces 0.3 apart when closed
- Motion (manifold3d sweep): closed 0 overlap; 1-2 deg the hook rides 0.42 over the bead (the click), clear from 3 deg; 6-105 deg free; stops on the base at about 110 deg; axial play about 0.35 before the cones take the lid
- printcheck: pass; the lower lid on the bed, the upper lid captured on its hinge (needs support); warnings: overhang (the upper lid's underside, about 240 mm2), thin bead and hook tips
- Bed: 40 x 23.15 x 53 in 180 x 180 x 180

## 8. Print setup

- Printer and settings: 180 x 180 x 180 bed, 0.4 nozzle, 0.2 layer, **PLA**, quantity **1 per plate**.
- Supports: **under the upper lid only** (tree support, or a support enforcer; it stands on the lower lid). Check in the slicer preview that no support goes into the hinge or latch gaps.
- Orientation: upright as used, on the plate's bottom edge (rack pins sideways, layers along them); lids printed closed on their hinges; the lower lid stands on the bed, the upper lid needs slicer support under it (it rests on the lower lid); 45 deg wings under the upper loop base.

## 9. Assumptions

- A1: one loop centred on each rack pin (user).
- A2: loop 40 wide (user), 14 tall (user rev 6); cable space depth = reference + 2 mm (user).
- A3: rev 6 (user): print in place, upright; support only under the upper lid (it stands on the lower lid). Rev 5 drop-on lids broke while fitting (user).
- A4: hinge tighter (user): cone clearance 0.25; the lid has about 0.35 axial play before the cones take it.
- A5: rev 7 latch after seba-med-cap (user): 45/45 bead on the post, 45/45 hook on a 1.0 arm; rev 8 bead 0.75 (user: raise it); rev 9 bead 1.05, 0.75 travel (user: tighter by 0.3; arm strain about 4.6 %, test it); no preload, because the lid prints closed and the hook must print 0.3 clear of the bead.

## 10. Open questions

| ID | Question | Blocking | Answer |
|---|---|---|---|
| Q1 | Cable size? | yes | reference cavity + 2 mm (user) |
| Q2 | Each loop centred on its pin? | yes | yes (user) |
| Q3 | Quantity per plate? | no | one per plate (user) |
| Q4 | Loop width? | yes | 40 mm overall (user, rev 2) |
| Q5 | Separate lids or print in place, and orientation? | yes | rev 4: print in place on its back; rev 5: upright, no support, lids drop on (user) |
| Q6 | Latch? | yes | rev 4 printed too loose (user): barb +0.05 |
| Q8 | Latch click? | yes | use the seba-med-cap bead and hook (user, rev 7) |
| Q7 | Hinge? | yes | rev 6: print in place upright, 2 mm taller band, bigger and tighter hinge (user) |
