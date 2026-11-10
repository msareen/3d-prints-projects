# music-stand-plate: design specification

> Status: **confirmed**, revision 12. All dimensions in mm. Machine-readable twin:
> `spec.json` (same IDs). The model is built only from what is written here.

**Revisions:** rev 1 = first spec. rev 2 = mesh in the centre plate. rev 3 = tab 65, heights 105. rev 4 = extenders drop on from the top on dovetail rails. rev 5 = solid tab. rev 6 = fit test. rev 7 = slot back, M6 stud, nut recess, printed thumb nut. rev 8 = slot sized for the raised collar and measured rivets. rev 9 = 5 mm bridge at the tip. rev 10 = 3-plate 3MF. rev 11 = V 1 mm wider per side after the fit test. rev 12 = 4-plate system: the V is a separate part held by 2 dovetail keys and 2 printed M6 bolts + nuts; all plates 170 x 170 (430 x 170 total); fit test dropped.

## 1. Purpose and context

A music plate for an existing folding music-stand holder: a tapered sheet-metal channel, open at the top, with a threaded stud (thumb nut) near the top, two dome rivet heads further down and a curved support at the bottom end. The holder is fixed; the plate slides into it and the nut tightens it. The A1 mini bed (180 x 180 x 180) is too small for a whole plate, so the plate is 3 parts. Load: a few sheets or a book resting on the plate and the 10 mm lip.

## 2. Inputs reviewed

| File | Kind | What it shows / says | Usable for |
|---|---|---|---|
| `input/brief.md` | text | user's description: 3 sections because the A1 mini bed is small, standard music-plate size | holder and layout |
| `input/Suggested-Plate design_261110_111501.jpg` | sketch | hand sketch: stand holder (U channel with one hole = stud), connector plate with 8 holes and tapered fit-plate tab, and a 3-section assembly with 4 push-button holes per joint. Proportions are meaningless, only words count. | holder and layout |
| `input/20261110_110257.jpg` | photo | caliper 66.2 mm along channel length | holder and layout |
| `input/20261110_110315.jpg` | photo | caliper 44.5 mm outer width at the top; stud and two domes visible, curved support at the bottom | holder and layout |
| `input/20261110_110327.jpg` | photo | caliper 42.5 mm, outer width at mid length | holder and layout |
| `input/20261110_110346.jpg` | photo | caliper 38.0 mm, outer width at the bottom | holder and layout |
| `input/20261110_110352.jpg` | photo | caliper 44.0 mm, outer width near the top | holder and layout |
| `input/20261110_110441.jpg` | photo | caliper 10.1 mm, side wall height (outer) | holder and layout |
| `input/20261110_110514.jpg` | photo | caliper 10.1 mm, same measurement from another angle | holder and layout |
| `input/20261110_110530.jpg` | photo | no number; shows stud, two domes and thumb nut behind the channel | holder and layout |
| `input/20261110_110534.jpg` | photo | no number; same view | holder and layout |
| `input/20261110_110612.jpg` | photo | no number; side view of the channel and clamp head | holder and layout |
| `input/20261110_110614.jpg` | photo | caliper 66.4 mm, channel length | holder and layout |
| `input/20261110_115004.jpg` | sketch | user's dimensioned sketch of the channel: front 44.4 outer top, 37.6 inner top, 30.6 inner bottom, 37.9 outer bottom, 66.9 length; side 9.5; top view 9.5 each side, 15.9 wide x 1 high curved support at the bottom | holder and layout |
| `input/20261110_131610.jpg` | photo | channel with the stud removed and a ruler along the right side: stud hole with a raised collar about 6.4 mm, about 9.2 mm below the top; rivet domes about 36.3 and 57.8 mm below the top, 9.5 mm across; all on the centre line (scaled from the dome width, about 16.3 px/mm) | holder and layout |
| `input/20261110_125957.jpg` | photo | printed fit test (rev 6) with the stud position marked: about 9.7 mm below the tab root, on the centre line | holder and layout |
| `input/20261110_130026.jpg` | photo | the same, measured across: about 10.7 mm below the root, centred | holder and layout |
| `input/20261110_130155.jpg` | photo | caliper 5.9 mm across the stud thread (M6) | holder and layout |

The two sketches' proportions are not used; only their written numbers are.

## 3. Coordinate system and datum

- Origin: centre plate: middle of the bottom edge of the plate body, on its back face (the tab hangs below, towards -Y). Extender: its inner overlap edge, on the bottom edge of the back face.
- X: across the plate, left to right seen from the front
- Y: up the plate; the bottom edge and the tab are towards -Y (front elevation faces -Y)
- Z: up = print direction; the back face lies on the bed at Z = 0; the music face and the lip point up
- Front of the part faces -Y (this is the front elevation).

## 4. Overall description

A 4-plate music plate for an existing folding music-stand holder (tapered sheet-metal channel, M6 stud with a thumb nut, two rivet heads). A separate V part slides into the holder; its 50 mm tongue sits behind the centre plate, held by 2 dovetail keys in grooves in the plate's back and 2 printed M6 countersunk bolts with printed nuts. The 170 x 170 centre plate and two 170 x 170 extenders (dropped on from the top on dovetail rails) make a 430 x 170 mm plate with a 10 mm lip and a hex mesh. PLA on an A1 mini, one part per plate.

- **Centre plate**: 170 x 170 x 4 mm, 10 mm lip, hex mesh (12 mm holes, 3 mm ribs) except round the joints; 4 dovetail grooves in the back for the extender rails (x = +-55, +-75, open at the top, closed at y = 8); 2 dovetail key grooves for the V (x = +-13, open at the bottom edge, closed at y = 48); 2 M6 clearance holes (6.6 mm) on the centre line at y = 15 and 38 with 90 degree countersinks on the music face.
- **Extenders** (left and right, mirrored): 170 x 170 mm, 8 mm thick over the visible 130 mm, 10 mm lip, hex mesh; the inner 40 mm is a 4 mm strip behind the centre plate with a 4 mm rebate and 2 dovetail rails. They drop on from the top and rest on the closed groove ends.
- **V** (separate part, rev 12): the tested V (65 mm long, 38.4 mm wide at the root, 32.1 at the tip, 4 mm; 7.4 mm stud slot, 11 mm through the rivet range, 5 mm bridge at the tip with a 4 mm gable relief behind and a 7 mm boss in front; 17 x 2 mm nut recess) with a 50 x 44 mm tongue above it that sits flat behind the centre plate. Two dovetail keys on the tongue front slide up into the plate's key grooves and stop at their closed ends; 2 printed M6 x 10 countersunk bolts (4 mm hex key) go in from the music face into 2 printed M6 nuts (10 AF x 3.2) held in 2 mm hex pockets on the back of the tongue. A printed M6 thumb nut fits the stand's stud.
- Assembled 430 x 170 mm plate, V below it. Edge treatment: R3 outer corners, 0.4 mm bottom elephant-foot chamfer on the bed face.

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source | Model param |
|---|---|---|---|---|---|---|---|---|
| D1 | holder channel length | 66.4 | ±0.3 | measured | medium | yes | photos 110614 = 66.4, 110257 = 66.2; sketch 115004 says 66.9 (conflict, 66.4 used, to be confirmed) | CH_LEN |
| D2 | holder inner width at the top (open) end | 37.6 | ±0.2 | measured | high | yes | input/20261110_115004.jpg: '37.6' arrow just below the top edge | CH_IN_TOP |
| D3 | holder inner width at the bottom end | 30.6 | ±0.2 | measured | high | yes | input/20261110_115004.jpg: '30.6' near the bottom | CH_IN_BOT |
| D4 | holder outer width at the top | 44.4 | ±0.2 | measured | high | no | sketch 115004 '44.4'; photo 110315 44.5, 110352 44.0 (reference only) |  |
| D5 | holder outer width at the bottom | 37.9 | ±0.2 | measured | high | no | sketch 115004 '37.9mm'; photo 110346 38.0 (reference only) |  |
| D6 | holder channel depth (usable) | 9.5 | ±0.2 | measured | medium | yes | sketch 115004 side '9.5mm' and top view '9.5'; photos 110441/110514 read 10.1 on the outer edge | CH_DEPTH |
| D7 | bottom curved support width | 15.9 | ±0.3 | measured | medium | no | sketch 115004 top view '15.9' with arrow 'At Bottom' |  |
| D8 | bottom curved support height (into the channel) | 1.0 | ±0.3 | measured | low | no | sketch 115004 top view, small '1' beside the half-circle | CH_STOP_H |
| D9 | stud distance from the top end of the channel | 9.5 |  | measured | medium | yes | fit-test marks 9.7 mm (photo 125957) and 10.7 mm (photo 130026) below the tab root, photo 131610 about 9.2 mm; 9.5 used and the slot runs 1 mm further (D55), so 8.5 to 10.7 are all clear | STUD_POS |
| D10 | stud diameter | 5.9 |  | measured | high | yes | caliper 5.9 mm across the stud thread (photo 130155): M6 | STUD_D |
| D11 | dome rivet 1 distance from the top end | 36.3 |  | measured | medium | no | photo 131610, ruler along the channel, scaled from the 9.5 mm dome width | DOME1_POS |
| D12 | dome rivet 2 distance from the top end | 57.8 |  | measured | medium | no | photo 131610, ruler along the channel | DOME2_POS |
| D13 | dome rivet head diameter | 9.5 |  | measured | medium | no | photo 131610: dome 155 px across at about 16.3 px/mm | DOME_D |
| D14 | dome rivet head height | 2.0 |  | estimated | low | no | side photos 110612/110530, not measurable | rev 7: the dome slot is back | DOME_H |
| D15 | tab clearance per side in the channel | 0.3 |  | default | high | no | user: a slightly loose fit is fine, the nut tightens the plate (FITS free = 0.30 mm per side) |  |
| D16 | tab length (below the plate) | 65.0 | ±0.3 | derived | medium | yes | D1 - D8 (stop) = 65.4 is where the tip stops; 65.0 leaves 0.4 mm at the tip so the plate edge rests on the channel top (found in the insertion sweep, rev 3) | TAB_L |
| D17 | tab thickness | 4.0 |  | derived | high | yes | = D18. rev 7: the slot is back (the solid tab was pushed up by the stud), so the tab sits on the floor and the stud comes through for the nut | TAB_T |
| D18 | plate thickness | 4.0 |  | given | high | no | user answer: PLA, 4 mm | PLATE_T |
| D19 | centre plate width | 170.0 | ±0.3 | default | high | no | A1 mini bed 180 minus 10 margin | PLATE_W |
| D20 | centre plate height (above the tab) | 170.0 | ±0.3 | default | high | no | rev 12: the V is a separate part, so the plate uses the 170 the bed allows (5 mm margin per side) | PLATE_H |
| D21 | bottom lip projection (towards the music) | 10.0 |  | given | high | no | user answer: yes, 10 mm lip | LIP_H |
| D22 | bottom lip thickness | 4.0 |  | default | high | no | = D18 | LIP_T |
| D23 | overlap length (extender strip behind the centre plate) | 40.0 |  | given | high | no | user: overlap for maximum strength; recommended option chosen: behind the centre plate, 40 mm | OVERLAP |
| D24 | extender width beyond the centre plate edge | 130.0 |  | given | high | no | rev 12: full size: extender 170 wide = 40 overlap + 130 visible; total 170 + 2 x 130 = 430 | EXT_VIS_W |
| D25 | extender main thickness | 8.0 |  | derived | high | no | 2 x D18: 4 mm behind the centre-plate plane + 4 mm in the music plane | EXT_T |
| D26 | extender rebate depth (the centre plate's edge sits in it) | 4.0 |  | derived | high | yes | = D18 + clearance, so the fronts are flush | REBATE_D |
| D27 | extender height (full square, same as the centre plate) | 170.0 |  | given | high | no | rev 12: = D20 | EXT_H |
| D33 | corner radius | 3.0 |  | default | high | no | no corner treatment in the sketch | CORNER_R |
| D34 | mesh hole size (hexagon, across flats) | 12.0 |  | default | medium | no | user: chicken-net holes in the side plates to save material, thick but not super strong | MESH_AF |
| D35 | mesh rib width between holes | 3.0 |  | default | medium | no | about 7 perimeters at 0.4 mm nozzle; thick, as the user wants | MESH_RIB |
| D36 | solid border around the mesh (outer edges and the strip) | 8.0 |  | default | medium | no | keeps edges stiff; the 40 mm overlap strip stays fully solid | MESH_BORDER |
| D37 | rail neck width (base of the dovetail) | 5.0 |  | default | medium | no | user, rev 4: the side plates must come on from the top so gravity helps hold them (replaces the push-in pegs) | RAIL_NECK |
| D38 | rail head width (top of the dovetail) | 8.0 |  | default | medium | no | user, rev 4: the side plates must come on from the top so gravity helps hold them (replaces the push-in pegs) | RAIL_HEAD |
| D39 | rail height above the strip face | 2.4 |  | default | medium | no | user, rev 4: the side plates must come on from the top so gravity helps hold them (replaces the push-in pegs) | RAIL_H |
| D40 | first rail centre from the centre plate side edge | 10.0 |  | default | medium | no | user, rev 4: the side plates must come on from the top so gravity helps hold them (replaces the push-in pegs) | RAIL_EDGE0 |
| D41 | rail pitch (second rail further in) | 20.0 |  | default | medium | no | user, rev 4: the side plates must come on from the top so gravity helps hold them (replaces the push-in pegs) | RAIL_PITCH |
| D42 | rail bottom end = closed groove bottom (y from the plate bottom edge) | 8.0 |  | default | medium | no | user, rev 4: the side plates must come on from the top so gravity helps hold them (replaces the push-in pegs) | RAIL_Y0 |
| D43 | gap from the rail top end to the extender top edge | 8.0 |  | default | medium | no | user, rev 4: the side plates must come on from the top so gravity helps hold them (replaces the push-in pegs) | RAIL_TOP_GAP |
| D44 | lead-in chamfer at the tab tip (back edge, 45 deg) | 2.0 |  | default | medium | no | rev 5 lead-in; kept in rev 7 for easier entry | TAB_LEADIN |
| D47 | M6 thread pitch (coarse) | 1.0 |  | default | medium | no | rev 7: M6 standard coarse pitch; not measured | THREAD_P |
| D48 | thumb nut outside diameter | 16.0 |  | default | high | no | rev 7: user: print a nut of this thread to test the sample | NUT_OD |
| D49 | thumb nut height | 8.0 |  | default | high | no | rev 7: 8 thread turns | NUT_H |
| D50 | nut recess diameter in the tab front | 17.0 |  | default | high | no | rev 7: nut OD 16 + 1 | NUT_RECESS_D |
| D51 | nut recess depth | 2.0 |  | default | medium | no | rev 7: leaves 2 mm of tab under the nut, so more stud thread reaches the nut | NUT_RECESS_DEPTH |
| D52 | stud slot extra width (over the raised collar) | 1.0 |  | default | high | no | rev 8: the slot must clear the raised collar around the stud hole (6.4 mm, photo 131610), 0.5 mm per side -> 7.4 mm | STUD_SLOT_EXTRA |
| D53 | dome slot extra width (over the dome diameter) | 1.5 |  | default | high | no | rev 7: 11 mm slot over the dome range | DOME_SLOT_EXTRA |
| D54 | raised collar around the stud hole, diameter | 6.4 |  | measured | medium | no | photo 131610: ring about 105 px across at about 16.3 px/mm | COLLAR_D |
| D55 | slot overrun past the measured stud and dome 1 | 1.0 |  | default | high | no | rev 8: margin for the photo scaling (stud 9.2 to 10.7) | SLOT_OVERRUN |
| D56 | bridge closing the slot at the tab tip, length | 5.0 |  | given | high | no | rev 9: user, rev 9: join 5 mm from the bottom to make it stronger | BRIDGE_L |
| D57 | gable relief under the bridge (back face), peak height | 4.0 |  | default | medium | no | rev 9: gable (no flat roof); clears a 9.5 x 2 mm dome cap and the 6.4 x 1.5 mm collar everywhere across its width | BRIDGE_RELIEF |
| D58 | tab thickness at the tip boss | 7.0 |  | default | medium | no | rev 9: 3 mm of bridge over the 4 mm relief peak; 7 mm leaves 2.5 mm in the 9.5 mm channel | TIP_BOSS_T |
| D59 | tip boss width (centred) | 15.0 |  | default | medium | no | rev 9: clear of the channel's side lips | TIP_BOSS_W |
| D60 | tip boss length from the tip | 8.0 |  | default | medium | no | rev 9: covers the 5 mm bridge + 3 mm | TIP_BOSS_L |
| D61 | gable relief width at the back face | 13.0 |  | default | medium | no | rev 9: faces atan(4 / 6.5) = 31.6 deg from horizontal, 58.4 deg from vertical (limit 60) | RELIEF_W |
| D62 | tab widening per side after the fit test | 1.0 |  | given | high | yes | user, rev 11, after printing the fit test: 'fit is good, increase the V 1 mm from both sides for a snugger fit'. The tab is now 0.7 mm per side wider than the sketched inner widths (37.6 / 30.6), so the channel is roomier at the tab than those numbers | TAB_WIDEN |
| D63 | V tongue length above the V root (behind the centre plate) | 50.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | TONGUE_L |
| D64 | V tongue width | 44.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | TONGUE_W |
| D65 | dovetail keys on the tongue front, x position (+-) | 13.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | KEY_X |
| D66 | lower bolt, height above the plate bottom edge (centre line) | 15.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | BOLT_Y1 |
| D67 | upper bolt, height above the plate bottom edge (centre line) | 38.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | BOLT_Y2 |
| D68 | printed M6 countersunk bolt, overall length | 10.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | BOLT_L |
| D69 | bolt head diameter (90 deg countersunk) | 12.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | BOLT_HEAD_D |
| D70 | printed M6 nut, across flats | 10.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | JAM_AF |
| D71 | printed M6 nut, thickness | 3.2 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | JAM_T |
| D72 | nut pocket depth in the back of the tongue | 2.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | JAM_POCKET |
| D73 | hex key socket in the bolt head, across flats | 4.0 |  | default | medium | no | rev 12: user asked for a separate V held by 2 printed M6 bolts and nuts, going a little deep into the main plate with a key groove | BOLT_HEX |

Basis: `given`, `measured`, `derived`, `estimated` (scaled from a photo), `default`.

## 6. Features

| ID | Feature | Count | Position (from datum) | Dimensions | Notes |
|---|---|---|---|---|---|
| F1 | tapered tab | 1 | x = 0 centred, hangs below the plate from y = 0 to y = -65 | D2, D3, D15, D16, D17, D44, D62 | 4 mm, on the channel floor; width = channel inner width - 0.3 + 1.0 mm per side (rev 11, from the fit test): about 38.4 mm at the root, 32.1 mm at the tip; 2 mm lead-in at the tip |
| F2 | stud slot in the tab (narrow) | 1 | x = 0; from the tab tip up to 1 mm past the stud (slot end centre 8.5 mm below the channel top) | D9, D10, D52, D54, D55 | rev 8: 7.4 mm wide, clears the raised collar (6.4) around the stud; the nut clamps the tab around it; rev 9: closed at the tip by the 5 mm bridge |
| F3 | dome slot (wider part of the slot) | 1 | x = 0; from the tab tip up to 1.75 mm past the top edge of rivet 1 (D11) | D11, D12, D13, D53, D55 | 11 mm wide, through; ends 21 mm below the stud so the nut bears on solid tab; rev 9: closed at the tip by the 5 mm bridge |
| F4 | dovetail grooves in the back face of the centre plate | 4 | 2 per side, centre lines 10 and 30 mm from the side edge, from y = 8 up to the top edge (open at the top, closed at the bottom) | D37, D38, D39, D40, D41, D42 | the extender's rails slide in from the top; the closed bottom end carries the weight; groove = rail + 0.2 mm per side |
| F5 | bottom lip | 3 | along the bottom edge of every part, y = 0..4, full width | D21, D22 | protrudes up (towards the music) 10 mm |
| F6 | extender rebate and strip | 2 | inner 40 mm of each extender, front face recessed 4 mm | D23, D25, D26 | the centre plate edge sits in the rebate; fronts end up flush |
| F7 | dovetail rails on the extender strip | 4 | 2 per extender, mirrored positions of F4, from y = 8 to 8 mm below the top edge, standing on the rebate floor | D37, D38, D39, D40, D41, D42, D43 | overhang of the head is about 31 degrees from vertical, so it prints without support |
| F8 | full-height square outline | 2 | extender is a 130 x 105 rectangle: x from the overlap inner end (45 from the centre line) to 175, y = 0 to 105 | D24, D27 | the user chose a full square with the mesh over sloped wings; corners R3 on the outer end |
| F9 | hex mesh (chicken net) through holes | 2 | inside the visible 90 mm of each extender, D36 away from its outer edge, the sloped edge, the lip and the overlap strip, in a hex pattern | D34, D35, D36 | through the 8 mm thick main body; centre plate stays solid; lip stays solid |
| F10 | hex mesh in the centre plate | 1 | x within +-37 of the centre line (the 40 mm peg-hole zones and D36 border stay solid), y from the lip border to the top border; the tab and lip stay solid | D34, D35, D36, D23 | user request, revision 2: mesh also in the centre plate except where it has holes |
| F12 | nut recess | 1 | tab front face, centred on the stud | D50, D51 | 17 mm, 2 mm deep |
| F13 | printed M6 thumb nut (test part) | 1 | separate part, next to the fit test in the model files | D10, D47, D48, D49 | right-hand ISO M6x1 internal thread + 0.3 mm radial clearance, 45 deg entry chamfers, 10 grip notches |
| F14 | tip bridge with back relief and front boss | 1 | tab tip, y = -65 to -60 (bridge), boss 15 mm wide from -65 to -57 | D56, D57, D58, D59, D60, D61 | joins the two legs; 13 mm wide, 4 mm high gable relief on the back so it rides over the collar and the domes; 7 mm thick, 15 mm wide boss on the front keeps 3 mm of bridge over the peak |
| F15 | V tongue with 2 dovetail keys | 1 | V part, y = 0 to 50 above the V root, 44 mm wide; keys at x = +-13 from y = 2 to 48 on the front | D63, D64, D65, D37, D38, D39 | the tongue sits flat behind the centre plate; the keys (same profile as the extender rails) go 2.4 mm into the plate |
| F16 | key grooves and countersunk bolt holes in the centre plate | 1 | plate back, x = +-13, open at the bottom edge, closed at y = 48; bolt holes on the centre line at y = 15 and 38 | D65, D66, D67, D69 | the V slides up into the grooves until the keys stop at the closed ends; 6.6 mm holes, 90 deg countersinks on the music face |
| F17 | 2 printed M6 countersunk bolts | 2 | separate parts, printed head down | D68, D69, D73, D47 | M6 x 1, 0.2 mm smaller per side than nominal, 4 mm hex key socket, chamfered tip |
| F18 | 2 printed M6 nuts in hex pockets on the back of the tongue | 2 | V back, at the bolt positions | D70, D71, D72 | 10 mm across flats, 3.2 mm thick; 2 mm in the pocket so they do not turn, 1.2 mm stand out behind |

## 7. Consistency checks

- Assembled width: 170 (centre) + 2 x (170 - 40 overlap) = 170 + 260 = 430 ✓.
- Overlap: the strip reaches 45 from the centre line; the rails and grooves sit at 55 and 75 from the centre line (head width 8 -> 51..59 and 71..79), inside the 45..85 overlap ✓; the grooves leave a 1.4 mm front skin on the 4 mm plate.
- Bed: centre 170 x 170, extenders 170 x 170, V 44 x 115: all <= 170 (180 bed, 5 mm margin) ✓.
- Thickness: extender 8 = 4 (behind) + 4 (music plane) = 2 x D18 ✓; the rebate 4 = plate thickness (+ fit clearance).
- V fit: widths = channel inner width - 0.3 + 1.0 per side (rev 11 fit test) = 38.4 at the root, 32.1 at the tip; checked by the user's fit test.
- Conflicts: channel length 66.4 (photos) vs 66.9 (sketch) -> Q2; channel depth 9.5 (sketch) vs 10.1 (photos, outer edge).
- Joint: keys 2..48 on the tongue = grooves -1..48 in the plate; bolt holes at 15 and 38 sit between the keys (13 - 4.2 = 8.8 > 6.3 countersink radius) ✓. Bolt 10 = head 3 + plate 1 + tongue 2 + nut 3.2 + 0.8 out ✓.

## 8. Print setup

Printer bed [180, 180, 180] (A1 mini), nozzle 0.4, layer 0.2, material PLA, supports: none. Orientation: back face flat on the bed, music face and lip pointing up; no supports (the extender's rebate faces up). Quantity: one set (centre + 2 extenders). Fits: tab sliding (loose, 0.3 mm per side), rails sliding (0.2 mm per side, drops on under its weight).

## 9. Assumptions

1. A1: PLA on a Bambu A1 mini (180 x 180 x 180), 0.4 mm nozzle, 0.2 mm layers, no supports. If the bed differs, the 170 mm long centre plate (plate + tab) may not fit.
2. A3: the channel's usable inner widths are the user's 37.6 and 30.6 (not the outer 44.4 / 37.9). The tab is made 0.3 mm smaller per side on both widths.
3. A6: all extenders are a left/right pair, printed once each.
4. A7: the model files lay the three parts out side by side (extenders moved 50 mm out) so the drawings and the viewer show a print layout; the assembled position is in the datum and the section views. Slicers re-place the parts anyway.
5. A8 (rev 2): centre plate mesh uses the same hole size, rib and border (D34-D36), 5 columns across x = -37..37; it stops D36 away from the peg-hole zones and above the lip.
6. A9 (rev 3): from the insertion sweep, the tab is 65 mm and the plates 105 mm tall, so the plate bottom edge rests on the channel top and the tab tip stops 0.4 mm short of the curved support. A channel of 66.9 mm leaves 0.9 mm at the tip.
7. A10 (rev 4): the extenders drop on from the top. 2 dovetail rails per extender (5 mm neck, 8 mm head, 2.4 mm high) slide down into grooves in the centre plate's back face; the grooves are closed at the bottom (y = 8), so gravity seats the extender and the paper weight loads the joint in compression. The groove leaves a 1.4 mm front skin on the 4 mm plate. No snap detent: add a dab of glue or a small bump later if it lifts out.
8. A5 (replaced in rev 4): the push-in pegs were dropped.
9. A12 (rev 7): the solid tab was pushed up by the stud on the printed test, so the slot is back, narrowed to the measured M6 stud. The nut screws onto the stud through the slot; a 2 mm recess lets it reach more thread. How far the stud stands out was not measured.
10. A13 (rev 7): the printed nut assumes M6 x 1.0 (coarse). Its thread flanks are 60 degree overhangs (ISO profile), which the A1 mini prints at this size; OVERHANG_LIMIT is 60 for that reason and the plates were checked at 45.
11. A14 (rev 8): photo 131610 shows the raised collar round the stud hole and the two rivet domes. The narrow slot is sized for the collar (7.4 mm) and both slot ends run 1 mm past the measured positions.
12. A15 (rev 9): with the slot closed at the tip, the stud (bolt) must be taken out before the tab slides in, then pushed back through the slot from behind and the nut fitted. The bridge rides over the domes and the collar: if the domes are taller than 3 mm, the relief must be deeper.
13. A16 (rev 10): the final 3MF has 3 plates (centre, left extender, right extender) for Bambu Studio / OrcaSlicer; the fit test and the nut are only in the separate test-plate 3MF.
14. A17 (rev 11): tab widened 1 mm per side after the physical fit test; the sweep checks the stud, collar, domes and the stop, and the side walls were checked by the user's test print.
15. A18 (rev 12): the V is a separate part. The chosen 'thickened pad with a socket on the back of the centre plate' cannot print with the plate's back on the bed (the pad would stick out below the bed face, a back socket needs a 40 mm flat roof), so the V's tongue sits behind the plate and goes into it with 2 dovetail keys in grooves (2.4 mm deep) instead, plus 2 printed M6 bolts. Printed M6 threads are weak: the keys carry the load, the bolts only clamp.

## 10. Open questions

| ID | Question | Blocking | Answer |
|---|---|---|---|
| Q1 | Stud distance from the top end, stud diameter, both dome rivet distances and the dome head size and height (D9-D14) are photo estimates. Please confirm or measure. | no | User confirmed on 2026-11-10: use the photo estimates (D9-D13). Slot and pockets are generous. |
| Q2 | Channel length: photos say 66.2 / 66.4, the sketch 66.9. Which should I use? | no |  |
| Q4 | Keep the sloped outer edge on the extenders, or use a full-height square now that the hex mesh saves the material? | no | Full square with the mesh; 12 mm holes are fine (user, 2026-11-10) |
| Q3 | How far does the stud stick up above the channel floor (for a 4 mm tab plus a nut)? | no |  |
