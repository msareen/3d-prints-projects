## Parts and plates

`music-stand-plate-PLA.3mf` has 5 plates (Bambu Studio). Open it as a project (double-click it, or File > Open Project; if Bambu Studio asks, choose to open it as a project, not "import geometry only"). It selects the Bambu Lab A1 mini 0.4 nozzle, 0.20mm Standard @BBL A1M and Bambu PLA Basic @BBL A1M presets on the Textured PEI plate; change the filament if you use another PLA. `music-stand-plate-PLA-plates.svg` shows what each plate should look like.

1. `centre` (170 x 170 mm)
2. `extender-left` (170 x 170 mm)
3. `extender-right` (170 x 170 mm)
4. the `v-tab` with the small parts: 2 printed M6 bolts (`bolt-1`, `bolt-2`), 2 printed M6 nuts (`jam-nut-1`, `jam-nut-2`) and the thumb `nut` for the stand's stud
5. the extender lock bolts (rev 13): `bolt-3`, `bolt-4`, `jam-nut-3`, `jam-nut-4` (same as bolt-1 / jam-nut-1)

Rev 14 changes only the paper stop on the centre plate and the two extenders: 13 mm deep (was 10) with a gentle 2 mm upward J curl at its end. Plates 4 and 5 are the same as rev 13: if you have them, print plates 1, 2 and 3. Rev 13 and rev 14 plates fit each other (the joints did not change), so you can also replace them one at a time.

All plates: back face on the bed, music face and paper stop up, no supports. The J curl leans at most 27 degrees from vertical, so it prints without support.

Bolts and nuts: 4 walls or 100 % infill, slow outer walls. The bolts print head down.

## Assembly

1. Drop the two printed M6 nuts into the hex pockets on the back of the V's tongue.
2. Slide the V's tongue up behind the centre plate's bottom middle, the two keys in the two grooves in the plate's back, until the keys stop at the closed ends.
3. Put the 2 countersunk bolts in from the music face and tighten them with a 4 mm hex key, into the nuts. Do not overtighten: printed threads strip. The keys carry the load, the bolts only hold the V in place.
4. On the stand: take the knurled nut off and push the stud out of the holder. Slide the V into the holder from the top: the bridge at the tip rides over the raised collar and the two rivet heads. The plate's bottom edge comes to rest on the top of the metal channel.
5. Push the stud back through from behind, through the slot, and screw the thumb nut on into the 17 mm recess.
6. Hold each extender above the centre plate, its two rails over the open top ends of the grooves in the back of the centre plate, and lower it straight down until it stops. The fronts end up flush.
7. Lock each extender: hold a printed nut in the hex pocket on the back of the extender's strip, put a countersunk bolt in from the music face (the hole 20 mm in from the centre plate's side edge, half way up) and tighten it with the 4 mm hex key, snug only. To remove an extender, take the bolt out and lift it straight up.

## Fits to check

- Rev 13 print: every part fitted (user, 2026-11-11). The values below are the ones that fitted.
- V in the holder: as tested (1 mm wider per side than the first fit test). If too tight, take it back in 0.25 mm steps.
- V keys and extender rails in their grooves: 0.2 mm clearance per side. If tight, loosen in 0.05 mm steps (sliding clearance in `fits-PLA.json`); if they wobble, tighten in 0.05 mm steps. FDM adds about 0.1 mm per side, so a first print may be tight.
- Printed bolts and nuts (all 4 sets): M6 x 1.0, 0.2 mm smaller (bolt) and larger (nut) per side than nominal, with extra flank clearance. If they bind, open the clearance in 0.05 mm steps; if they skip, close it.
- The thumb nut on the stand's stud: as before (M6 x 1.0 assumed for the stud).

## Accepted warnings

- `thin_walls` on the plates and the V: a few samples on the sharp corners of the dovetail flanks and the tip lead-in edge. Real walls are at least 1.35 mm (skin above a groove) and 3 mm (mesh ribs). Accepted.
- `thin_walls` and `small_holes` on the bolts and nuts: thread ridges come to a point and the gaps between turns are read as small holes. Expected for threads. Accepted.
- Overhang limit is 60 degrees in build.py. Two features need it: the thread flanks of the bolts and nuts (about 51 degrees), and the gable relief behind the V's tip bridge (about 58 degrees, a 4 mm high, 5 mm long roof). The centre plate and both extenders pass at 45 degrees.
- The 1.35 mm skin above a groove prints as about 3 perimeters: do not use fewer than 3 walls.
