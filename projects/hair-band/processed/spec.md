# hair-band: design specification

> Status: **confirmed**, revision 4. All dimensions in mm. Machine-readable twin: `spec.json` (same IDs).

Revisions:
- rev 1 (2026-11-14): drafted from four photos of the user's chain-link headband; sizes from the photo (user's choice), teeth 1.4 (user), PETG + PLA, 180 mm bed; confirmed (user: "generate the render").
- rev 2 (2026-11-14): openings blind from outside, flat-faced links with chamfers (printability). Superseded by rev 3.
- rev 3 (2026-11-14): user: "the braided chain like design did not came", "it is more squarish". The links are now round oval wire loops like the original, slanted and twisted so they interlock, with see-through openings; a hidden 50° keel under every wire and tooth makes them print flat without supports. Deleted D9-D12 and D20-D26 (flat links, chamfers, blind openings); added D27-D31. Built: 43 links at 9.018 and 76 teeth. Tooth tip ends exactly D14 beyond the inner face. Confirmed (user: "create output").
- rev 4 (2026-11-14): user, after printing rev 3: "too much support because of hanging teeth, but I need that", "too flexible, I need little bit hard", "make the last end little smooth, it is poking against skin". Added a hidden 2.6 mm spine on the inner face (D32, D33; F5): it stiffens the band about 3x and carries every upper wire and tooth. Each tooth now grows out of the spine on a 50° web (D30), so a layer check finds nothing starting in mid-air (rev 3 had 291 such spots, the slicer supported them). The link openings become ~1.8 mm deep pockets from outside instead of see-through. Added a smooth rounded pad at each tip (D34; F4). Then, user: "can we still have some chain gaps": see-through windows in the spine behind the 20 links of the arms (D35, D36), each about 3.9 x 1.9 with a short bridged top; the toothed zone keeps a solid spine because each upper tooth's web stands right behind the link opening. Confirmed (user: "yes create output").

## 1. Purpose and context

A copy of the user's moulded chain-link headband ("need the same design"), with the grip teeth that matter most to the user. It is an open C band, widest about a third of the way down, with the arms curving in towards the tips. The band is a curb chain of round oval links: slanted, each one passing in front of the next, with openings through them. Over the top arc, two staggered rows of round pin teeth point at the head to hold the hair. A hidden solid spine along the inner face makes the band stiffer, and each tip ends in a smooth rounded pad. One piece, printed flat on the bed with no supports.

## 2. Inputs reviewed

| File | Kind | Notes |
|---|---|---|
| input/brief.md | text | the user's words and stage 1 answers |
| input/20261114_131012.jpg | photo | top view on the cutting mat; outline sizes scaled from the 1/2 inch grid |
| input/20261114_131024.jpg | photo | low side view of the outer face: round slanted curb links, see-through openings, round end link |
| input/20261114_131038.jpg | photo | close-up of the inner face: two staggered rows of pin teeth, 2 per link per row |
| input/20261114_131056.jpg | photo | oblique top view: braid-like crossing of the links; teeth over the top arc only |

No callouts or written numbers in any photo. Mat: the large grid is 1/2 inch (big numbers = inches, every second line); the edge rulers are cm. The top-view photo was measured by fitting the grid lines (rms < 1.5 px) and segmenting the black band.

## 3. Coordinate system and datum

- Origin: X = 0 on the mirror line between the tips; Y = 0 at the crown's outer face; Z = 0 on the bed
- X: across the band, ear to ear
- Y: from the crown towards the tips; the crown's outer face is the front (-Y)
- Z: up = print direction; the band lies flat as on a table, its height D3 is the Z extent

## 4. Overall description

**Outline (F1).** The band centreline is two half-ellipses meeting at the widest point, Y = D5 = 70. Both have the same X semi-axis, D1/2 + D6/2 = 60.2. The lower half closes towards the tips, gap D4 = 25 between the inner faces, and the tips reach Y = D2 = 147. The chain is D6 = 4.36 thick radially. Inside width at the widest point: D1 = 116. Envelope: 124.6 x 146.9 x 8.

**Chain (F2).** 43 identical links run tip to tip along the centreline at a pitch of 9.018 (D7 adjusted so whole links end at the tips), with the crown link in the middle. Each link is an oval loop of round wire, D27 = 2.4 thick and D8 = 14 long, filling the band height D3 = 8. It is slanted D28 = 15° in the face and twisted D29 = 10° about Z, so its leading end passes in front of the next link and its trailing end behind. That crossing gives the braid look of the original. Neighbours overlap by 5 and fuse where the wires cross. The openings are open from the outside. Over the toothed zone they are about 1.8 deep and closed at the back by the spine (F5); on the arms the spine has a see-through window behind each one.

**Spine (F5).** A solid wall D32 = 2.6 thick runs along the whole band on the inner side of the chain, its inner face flush with the band's inner face, from the bed to D33 = 7.6 with a round top. It fuses every link, so the band bends as one strip instead of a loose chain: about 3x stiffer. It also carries the keels of the upper wires, so nothing starts in mid-air. Near each tip it blends into the tip pad over 3 mm. On the arms, beyond the teeth, the spine has a see-through window behind every link (20 in all, about 3.9 long x 1.9 high), so you can still see through the chain there. Each window follows the link's clear opening D35 = 0.3 inside the wires; its top is flat for at most D36 = 1.6 (a short bridge, held on both sides) and slopes down at 50° beyond that, so it prints without supports. The toothed zone keeps a solid spine: each upper tooth's web stands on it right behind the link opening. The windows cost about 2 % of the stiffness: they sit where the bending load is small, near the tips.

**How it prints.** Under every wire there is a hidden keel: the wire section is a circle with a 50° V underneath (D30), like a teardrop pointing down. Seen from above and from outside, the wire is round. Nothing overhangs more than 40° from vertical, and every wire and tooth grows out of the spine or the bed layer by layer, so the band prints flat without supports. The lowest wire is cut flat 0.4 (D31) where it meets the bed.

**Grip teeth (F3).** Over D18 = 170 of centreline centred on the crown there are 76 teeth. Each link carries 2 teeth, D15 = 3 apart, in each of two rows: the lower row at Z = 1.0 and the upper row at Z = 6.7, shifted half a pitch (4.5) from each other. Each tooth is a round D13 = 1.4 pin, keeled underneath, with a rounded tip. It is rooted in the spine and points radially inward, D14 = 2.5 beyond the band's inner face. Under each tooth a web as wide as the tooth climbs at D30 = 50° from the spine face (3.0 below the tooth axis) to the tip, so seen from the side a tooth is a shark fin with a round top. The lower row's webs end on the bed.

**Tips (F4).** Each tip is a smooth rounded pad, D34 = 10 long, as thick as the chain (D6) and as high as the band (D3), rounded at the end and on its edges with radius D6/2 = 2.18. The last link runs into it; the wires and spine are trimmed inside the pad so nothing pokes through.

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source |
|---|---|---|---|---|---|---|---|
| D1 | inside width at the widest point (body, teeth excluded) | 116.0 | ±3 | estimated | medium | no | photo 131012 on the mat grid; user chose photo estimates |
| D2 | overall length, crown outer face to the tips (Y) | 147.0 | ±3 | estimated | medium | no | photo 131012: Y extent 145-148 |
| D3 | band height lying flat (Z) = link height | 8.0 | ±1 | estimated | medium | no | photo 131024: end link ~255 px at ~31 px/mm |
| D4 | gap between the tips, inner faces | 25.0 | ±4 | estimated | low | no | photo 131012: 24-28 |
| D5 | widest point from the crown outer face (Y) | 70.0 | ±5 | estimated | medium | no | photo 131012: width peaks at Y 60-76 |
| D6 | chain radial thickness (no teeth) | 4.36 |  | derived | medium | no | D27 + 2 x twist travel (5.65 x sin 10°) |
| D7 | link pitch (nominal; built 9.018 for whole links) | 9.0 | ±0.3 | estimated | medium | no | photo 131012: ~9.2 |
| D8 | link outer length along its own axis | 14.0 |  | estimated | low | no | photo 131024: overlap about 1/3 |
| D13 | tooth diameter | 1.4 |  | given | high | no | user; original ~1.1 |
| D14 | tooth length beyond the band's inner face | 2.5 |  | estimated | medium | no | photo 131038: ~2-2.5 |
| D15 | tooth spacing within a pair | 3.0 |  | estimated | medium | no | photo 131038 |
| D16 | lower tooth row axis Z | 1.0 |  | derived | high | no | in the lower wire; keel cut by the bed |
| D17 | upper tooth row axis Z | 6.7 |  | default | medium | no | in the upper wire |
| D18 | toothed length along the centreline, centred on the crown | 170.0 | ±15 | estimated | medium | no | photos 131012 / 131056: teeth stop ~15 above the widest point |
| D19 | upper / lower row offset along the band | 4.5 |  | derived | medium | no | D7 / 2 |
| D27 | link wire diameter | 2.4 |  | estimated | medium | no | photo 131024: rails ~2.5 |
| D28 | link slant in the face (deg) | 15 |  | estimated | medium | no | photo 131024; more slant closes the openings |
| D29 | link twist about Z (deg) | 10 |  | default | medium | no | curb / braid crossing; gives D6 |
| D30 | hidden keel slope under wires and teeth, and slope of the tooth webs (deg from horizontal) | 50 |  | default | high | no | 40° from vertical: no supports |
| D31 | lowest wire cut flat at the bed | 0.4 |  | default | medium | no | 2 layers of bed contact |
| D32 | hidden spine, radial thickness from the inner face | 2.6 |  | derived | high | no | rev 4 (user: stiffer, less support): smallest of 2.2 / 2.6 / 3.0 with nothing starting in mid-air |
| D33 | spine height (round top) | 7.6 |  | default | medium | no | under the 8 mm wire crowns, covers the upper tooth roots |
| D34 | rounded tip pad, length along the band | 10 |  | default | medium | no | rev 4 (user: tips poke the skin); end radius D6/2 |
| D35 | spine window clearance from every wire edge | 0.3 |  | default | medium | no | rev 4 (user: "some chain gaps"); 20 windows on the arms, ~3.9 x 1.9 |
| D36 | longest flat (bridged) window top | 1.6 |  | derived | high | no | printcheck bridge rule: ≤ 2/3 of the 2.6 spine depth; beyond it the top slopes at D30 |

No dimension is marked critical. The fit on the head depends on D1, D2 and D5, but the band flexes, and the user chose photo estimates over ruler measurements (A1).

## 6. Assumptions

- A1: D1, D2, D4 and D5 are scaled from the top-view photo (about ±3 mm); the user chose these. If the first print is too tight or too loose, measure the original with a ruler and change D1.
- A2: the mat grid is 1/2 inch (12.7 mm), not 1 cm.
- A3: rev 4: round interlocked links like the original, on a hidden spine; over the toothed zone the openings are ~1.8 deep pockets, on the arms each has a see-through window (about a third of rev 3's clear opening). The spine stiffens the band and gives every wire and tooth something to grow from, so the slicer has nothing to support.
- A4: printed in its relaxed shape, as it lies in the photo.
- A5: teeth 1.4 thick (user), round with a keel and rounded tips.
- A6: mirror-symmetric outline about X = 0; every link is twisted the same way along the band, as on a real chain.
- A7: PETG primary (flexes over the head); PLA is also released, but it is stiffer and can crack at the arms if opened wide.
- A8: two printcheck warnings are accepted. Thin walls: the keel edges under the upper wires (z ~4.9), outside the spine, printed as a single line. Small hole: one 0.3 mm sliver between a wire and the spine on the left arm (x -37, y 131), thinner than one line; the slicer fills it. Layer alignment: a few short flat stretches of the sloped window floors (e.g. z 2.305) fall between layers; the slicer rounds them.
- A9: stiffness: opening the PETG band 17 mm per side (a 150 mm head) strains the spine about 0.7 % (PETG yields at about 4 %), about 1 N clamping per side. More infill barely changes this, because the wires and spine are mostly perimeters. D32 is the stiffness setting.

## 7. Consistency checks

- Width: D1 + 2 x D6 = 116 + 8.7 = 124.7 outside width; photo outside width 125; model 124.6 ✓
- Body: D6 + D14 = 4.36 + 2.5 = 6.9 ≈ photo body + teeth 7 ✓
- Link: wire centre half-axes A = D8/2 - D27/2 = 5.8; B = 2.69 from D3, D28, D31; opening ~9.2 x 2.9 before the neighbours' ends ✓; overlap D8 - D7 = 5 > 0, so neighbours fuse ✓
- Teeth inside the wires: upper 6.7 within the upper wire (centre ~6.4 ± 1.2); lower 1.0 within the lower wire (centre ~1.2 ± 1.2) ✓
- Teeth zone: D18 / 2 = 85 ends ~15 above the widest point ✓ (photo)
- Print: 124.6 x 146.9 x 8 on a 180 x 180 bed ✓; D3 = 40 layers; D27 = 6 lines; D13 = 3.5 lines; D32 = 6.5 lines; 807 mm² bed contact
- Printcheck: watertight, one body, no overhang beyond 45°, all probes correct
- Supports: a layer-by-layer check (each 0.2 layer against the one below, grown by 0.4) finds 0 mm² held on one side only (rev 3: 205 spots under the upper wires and teeth); the 20 window tops are bridges of at most 2.7 mm, held on both sides ✓

## 8. Open questions

None.

## 9. Print setup

PETG (primary) and PLA, 0.4 nozzle, 0.2 layers, 180 x 180 x 180 bed, no supports. Printed flat, one per plate. The bed contact is the spine, the flattened bottom wire, the tip pads and the lower teeth (807 mm² in total); a 3 mm brim still helps the arm ends.
