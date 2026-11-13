# seba-med-cap: design specification

> Status: **confirmed**, revision 8 (2026-11-05). Rev 8 (user): plug bulb 5.0. The channel groove is lengthened so that the plug sits relaxed when shut.
> Revision 7 (2026-11-05). Rev 7 (user): plug bulb 5.3 was too tight, now 5.2 in both materials.
> Revision 6 (2026-11-05). Rev 6 (user, lid still loose): the plug is hollow (1.0 wall) and 3.0 long, with a 4.9 shank, a 5.3 bulb (PLA 5.2) and a taper to a 4.5 tip; the bulb clicks into a 5.2 groove inside the channel at depth 1.05-1.75.
> Revision 5 (2026-11-05). Rev 5 (user, after a PETG test print): PETG is now the primary material; seal tube 3.0 -> 4.0 against wobble; skirt +1.8 (the measured remaining gap) so it reaches the shoulder; lid plug press fit; latch bead 0.5 / preload 0.2 in PETG (PLA 0.4 / 0.15).
> Revision 4 (2026-11-05). Rev 4 (user): channel 4.0 -> 5.0, a spout ring round it standing in a 1.6 x 1.0 groove (flush with the deck, no supports), and a matching seal ring on the lid; plug 4.8.
> Revision 3 (2026-11-05). Rev 3 (user request after a test print): skirt extended 6.2 to 0.5 above the shoulder, lid plug fit snug (3.8), latch bead 0.4 with 0.1 hook preload.
> Revision 2 (2026-11-04). Rev 2: the push lid becomes a flip-top
> with a clip-on hinge and a snap latch (user request). Rev 1 was confirmed. All dimensions in mm. Machine-readable twin:
> `spec.json` (same IDs). The model is built only from what is written here.

## 1. Purpose and context

This is a replacement for the original blue flip-top cap (46.1 mm) of a white
lotion bottle with a snap-on neck. The printed cap has two pieces:

- a **base** that snaps over the neck bead and dispenses through a 4 mm channel;
- a **flip lid** that clips onto a hinge pin on the base and clicks shut with a
  latch.

The material is PLA. The loads are opening and closing the lid by its thumb
tab, and pulling the cap off the neck.

## 2. Inputs reviewed

| File | Kind | What it shows / says | Usable for |
|---|---|---|---|
| 20261104_074951.jpg | photo | caliper across the neck at the upper ribbed band: **19.5 mm** | D1 |
| 20261104_075007.jpg | photo | caliper across the neck at the ribbed band, another angle: **19.4 mm** | D1 (check) |
| 20261104_075017.jpg | photo | caliper across the neck at a narrower band: **18.6 mm** | D2 |
| 20261104_075055.jpg | photo | side profile of the neck, no scale. From the top down: a small raised ring, a plain band, vertical ribs, a segmented bead, the plain neck, the shoulder collar, and a raised lug on the shoulder | D3, D4, D6 estimates, features |
| 20261104_075137.jpg | photo | caliper across the outside of the original cap: **46.1 mm** | D7 |
| 20261104_075156.jpg | photo | the original is a flip-top with a centre orifice | concept |
| 20261104_075221.jpg | photo | caliper across the original inner sleeve: **22.6 mm** | D8 (reference) |

## 3. Coordinate system and datum

- Origin: on the cap axis, on the cap's top face. The base prints **upside
  down**, so its top face lies on the bed.
- X: across the cap. The lid sits at x = D25 for layout, with its tab
  pointing +X.
- Y: across the cap (the part is round).
- Z: up, the print direction. For the base, +Z points from the top face
  into the cap, towards the bottle. The part sits on Z = 0.
- Front of the part faces -Y (this is the front elevation).

## 4. Overall description

The model is described closed and upright (bottle below). It is printed as
listed in §8.

**Base (F1 to F6, F9, F11).**
- A round deck, D7 = 46.1 across and D9 = 2.0 thick.
- An outer skirt (wall D11) runs down to a total height D13 = 17.1, 0.5 above
  the bottle shoulder; its rim is bevelled D44 to follow the shoulder slope.
- A coaxial snap sleeve (bore D27 = 21.4, OD D29 = 24.6) has a snap lip
  (ID D28 = 20.1) just below the bead, at D4. The lip has 45° faces on both
  sides, and six slots (D16 to D18) let the sleeve flex.
- A seal tube (D20 = 3.0) goes into the neck bore, and a D19 = 4.0 channel
  runs along the axis.

**Hinge (F9, F10).**
- On the −X side the base has two knuckles (D34 = 4 wide, D33 = 8 apart,
  D42 = 4 deep), joined by a D30 = 3.0 pin along Y.
- The pin's axis sits D31 = 3.3 outside the skirt and 1.05 below the top face.
- The pin is cut flat (D32 = 0.45) at the top-face level, so it prints lying
  on the bed with no overhang.
- The lid carries a C-clip (wall D35 = 1.2, bore 3.4) with a 45° mouth
  (D36 = 2.4) facing the bottle. The ring is cut flat 0.3 above its bore, so the horn
  tips are 0.9 wide instead of knife edges. To assemble:
  1. Open the lid flat (180°), so the mouth faces up.
  2. Press the clip down onto the pin.

**Lid (F7, F8, F10, F12).**
- A disc, D7 across and D21 = 2.0 thick, with a thumb tab at +X
  (D23 x D24).
- A short plug (D22 = 1.6, chamfered) goes into the channel. It is kept
  short because it swings in on an arc about the hinge.

**Latch (F11, F12).**
- A 45° bead (D38 = 0.3 high, D37 = 8 wide) on the skirt at +X, D39 = 4.0
  below the top face.
- A latch arm under the thumb tab (D40 = 1.0 thick, D41 = 0.2 off the skirt)
  ends in a 45° hook that clicks under the bead.
- Lifting the thumb tab releases it.

There are no internal anti-rotation ribs (A2).

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source | Model param |
|---|---|---|---|---|---|---|---|---|
| D1 | neck OD at the rib band | 19.5 | ±0.1 | measured | high | no | caliper 19.5 / 19.4 | |
| D2 | neck OD at the plain top band | 18.6 | ±0.1 | measured | high | no | caliper 18.6 | |
| **D3** | neck bead OD | 20.8 | ±0.1 | measured | high | **yes** | user caliper (photo estimate was 21.1) | BEAD_D |
| **D4** | top of neck to the underside of the bead | 7.0 | ±0.5 | given | medium | **yes** | photo estimate, accepted by the user as approximately right | TOP_TO_BEAD |
| **D5** | neck bore ID | 8.8 | ±0.1 | measured | high | **yes** | user caliper, inside jaws | BORE_D |
| **D6** | top of neck to the top of the shoulder lug | 9.4 | ±0.5 | given | medium | **yes** | photo estimate, accepted by the user as approximately right | TOP_TO_LUG |
| D7 | cap OD (base and lid) | 46.1 | ±0.3 | measured | high | no | caliper 46.1 | CAP_OD |
| D8 | original sleeve OD (reference) | 22.6 | | measured | medium | no | caliper 22.6 | |
| D9 | deck thickness | 2.0 | | default | high | no | 10 layers | DECK_T |
| D10 | sleeve wall | 1.6 | | default | high | no | 4 perimeters | SLEEVE_WALL |
| D11 | skirt wall | 1.6 | | default | high | no | 4 perimeters | SKIRT_WALL |
| D12 | clearance above the lug | 0.5 | | default | high | no | | LUG_CLEAR |
| D13 | base height (skirt outer edge) | 18.9 | | derived | medium | no | D9 + D6 − D12 + D43 | |
| D14 | snap undercut per side | 0.35 | | default | medium | no | PLA-friendly | SNAP_UNDERCUT |
| D15 | lip land height | 0.4 | | default | high | no | 2 layers | LIP_H |
| D16 | flex slots, count | 6 | | default | high | no | | SLOT_N |
| D17 | slot width | 1.2 | | default | high | no | 3 x nozzle | SLOT_W |
| D18 | slot length from the rim | 5.0 | | default | medium | no | | SLOT_L |
| D19 | channel diameter (rev 4) | 5.0 | | given | high | no | user: 1 mm more | CHANNEL_D |
| D20 | seal tube length (rev 5) | 4.0 | | default | high | no | | SEAL_L |
| D21 | lid disc thickness | 2.0 | | default | high | no | | LID_T |
| D22 | lid plug length (rev 6) | 3.0 | | given | high | no | user; arc shifts the tip ~0.06 | PIN_L |
| D23 | tab protrusion | 6.0 | | default | high | no | | TAB_OUT |
| D24 | tab width | 12.0 | | default | high | no | | TAB_W |
| D25 | lid layout offset X (rev 2) | 60.0 | | default | high | no | clears the hinge side | LID_OFFSET_X |
| D26 | foot chamfer | 0.4 | | default | high | no | elephant foot | FOOT_CHAMFER |
| D27 | sleeve bore | 21.5 PETG / 21.4 PLA | | derived | high | no | D3 + 2 x free (0.35 / 0.30) | |
| D28 | snap lip ID | 20.1 | | derived | high | no | D3 − 2 x D14 | |
| D29 | sleeve OD | 24.7 PETG / 24.6 PLA | | derived | high | no | D27 + 2 x D10 | |
| D30 | hinge pin Ø | 3.0 | | default | high | no | | PIN_HINGE_D |
| D31 | hinge axis outside the skirt | 3.3 | | default | high | no | clip radius 2.9 + 0.4 | HINGE_OFF |
| D32 | pin flat | 0.45 | | default | high | no | flat edge at 45°, prints on the bed | PIN_FLAT |
| D33 | gap between knuckles | 8.0 | | default | high | no | | HINGE_GAP |
| D34 | knuckle width | 4.0 | | default | high | no | | KNUCKLE_W |
| D35 | clip ring wall | 1.2 | | default | high | no | flexes 0.3 | CLIP_WALL |
| D36 | clip mouth | 2.4 | | derived | high | no | 2 x 1.7 x sin 45° | |
| D37 | latch width | 8.0 | | default | high | no | | LATCH_W |
| D38 | latch bead/hook depth (rev 5) | 0.5 PETG / 0.4 PLA | | default | high | no | strain 3.0 % / 2.4 % | LATCH_DEPTH |
| D39 | latch bead below the top face | 4.0 | | default | high | no | | LATCH_Z |
| D40 | latch arm thickness | 1.0 | | default | high | no | | LATCH_ARM_T |
| D41 | latch arm gap to the skirt | 0.2 | | default | high | no | | LATCH_GAP |
| D42 | knuckle depth | 4.0 | | default | high | no | | KNUCKLE_H |
| D43 | skirt extension (rev 5) | 8.0 | | measured | medium | no | 6.7 photo gap − 0.5, + 1.8 measured on the print | SKIRT_EXT |
| D44 | skirt rim bevel, inner edge higher (rev 3) | 1.0 | | estimated | low | no | ~32° shoulder across the wall | SKIRT_BEVEL |
| D46 | spout ring wall, OD 7.4 (rev 4) | 1.2 | | default | high | no | | SPOUT_WALL |
| D47 | groove width round the spout (rev 4) | 1.6 | | default | high | no | | GROOVE_W |
| D48 | groove depth (rev 4) | 1.0 | | default | high | no | | GROOVE_DEPTH |
| D49 | lid seal ring height, ID 7.6 (rev 4) | 0.8 | | default | high | no | snug on spout | RING_H |
| D50 | plug shank clearance per side, shank 4.9 (rev 6) | 0.05 | | default | high | no | | PLUG_SHANK_CLEAR |
| D51 | plug bulb OD (rev 8) | 5.0 | | given | high | no | user: 5.2 still tight; print adds ~0.1/side | PLUG_BULB_D |
| D52 | plug tip OD (rev 6) | 4.5 | | default | high | no | lead-in taper | PLUG_TIP_D |
| D53 | hollow plug wall, bore 2.9 (rev 6) | 1.0 | | given | high | no | user | PLUG_WALL |
| D54 | bulb land depth from the lid face (rev 6) | 1.2 | | default | high | no | land 1.2–1.6 | PLUG_BULB_Z |
| D55 | channel click groove OD (rev 6) | 5.2 | | default | high | no | 45° faces, depth 1.05–1.75 | CH_GROOVE_D |
| D45 | latch hook preload (rev 5) | 0.2 PETG / 0.15 PLA | | default | medium | no | lid was loose | LATCH_PRELOAD |

Fits come from FITS:
- the sleeve bore over the bead is **free** (0.30 per side);
- the seal tube in the bore is **snug** (0.10);
- the lid plug (rev 6): 4.9 shank (0.05 per side), 5.0 bulb (rev 8) clicking into a 5.2 groove that runs past the taper in the channel.

## 6. Features

| ID | Feature | Count | Position (closed, upright) | Dimensions | Notes |
|---|---|---|---|---|---|
| F1 | deck | 1 | top face | D7, D9, D26 | |
| F2 | outer skirt | 1 | coaxial, to D13 | D7, D11, D13 | clears the lug |
| F3 | snap sleeve + lip | 1 | coaxial | D3, D4, D10, D14, D15, D27–D29 | 45° lip faces |
| F4 | flex slots | 6 | equally spaced, from the sleeve rim | D16–D18 | |
| F5 | seal tube | 1 | coaxial, into the bore | D5, D19, D20 | snug |
| F6 | channel | 1 | on the axis | D19 | |
| F7 | lid disc + thumb tab | 1 | on the top face, tab +X | D7, D21, D23, D24 | |
| F8 | lid plug | 1 | lid axis | D19, D22 | sliding fit |
| F9 | knuckles + pin | 1 | −X, axis along Y | D30–D34, D42 | pin flat on the bed |
| F10 | lid C-clip | 1 | around the pin | D30, D33, D35, D36 | clip on with the lid opened flat |
| F11 | latch bead | 1 | +X on the skirt, D39 down | D37–D39 | 45° faces |
| F12 | latch arm + hook | 1 | +X under the tab | D37, D38, D40, D41 | 45° hook |

## 7. Consistency checks

- D1 19.5 vs 19.4: the two readings agree within 0.1 ✓. The larger is used.
- The bead must be wider than the ribs: D3 (20.8) > D1 (19.5) ✓.
- Plausibility against the original sleeve: original sleeve OD 22.6 minus
  2 x ~0.9 wall gives a bore of ~20.8, which matches the measured D3 ✓.

- Seal tube wall: (D5 − 0.2 − D19) / 2 = (8.6 − 4.0) / 2 = 2.3 ≥ 0.8 ✓.
- Plug vs channel: D22 1.6 < channel length 5.0 ✓. The plug tilts at most
  1.6 / 27 rad ≈ 3.4° while entering, and sliding clearance (0.2 per side)
  absorbs that ✓.
- Hinge clip clears the skirt: axis at 23.05 + 3.3 = 26.35. The clip's outer
  radius is 1.5 + 0.2 + 1.2 = 2.9, which leaves 0.4 to the skirt ✓.
- Clip grip: the pin is 3.0 and the mouth 2.4, so the clip snaps over
  0.3 per side ✓. Across the flat the pin is still 2.55 > 2.4 ✓.
- Latch arm strain: 3 x 1.0 x 0.3 / (2 x 5²) = 1.8 %, below the ~3 % PLA
  limit ✓.
- The lip has a 45° ramp of (D27 − D28) / 2 = 0.65, then the D15 land, then a 0.65
  lead-in. The sleeve rim sits at z = 2.0 + 7.0 + 0.65 + 0.4 + 0.65 = 10.7, inside the
  skirt height D13 = 10.9 ✓.
- Slots: D18 5.0 < sleeve length 10.7 − 2.0 = 8.7 ✓.
- Bed: 118 x 46 x 11 fits on 220 x 220 ✓.

## 8. Print setup

- Printer bed 220 x 220 x 250, 0.4 nozzle, 0.2 layer, **PETG** (primary) and **PLA**, no supports,
  quantity 1.
- **Base:** upside down, top face on the bed. The hinge pin lies on the bed
  on its 0.2 flat, and the snap lip and latch bead are 45° overhangs.
- **Lid:** outer face on the bed. The plug, the C-clip (mouth up) and the
  latch arm point up.
- Assembly: open the lid flat beside the base and press the clip onto the
  pin.

## 9. Assumptions

1. **A1:** the neck is a snap-on neck, not threaded. If it is threaded, the
   whole sleeve needs redesigning.
2. **A2:** nothing locks the cap's rotation (the cap is round and the
   channel central).
3. **A3:** the original valve insert is not reused; the lid plug closes the open channel.
4. **A4:** the seal is splash-tight, not pressure-tight (PLA is rigid).
5. **A5 (rev 3):** the shoulder lug lies inside the skirt bore, so the skirt runs
   down to 0.5 above the shoulder with no notch.

## 10. Open questions

| ID | Question | Blocking | Answer |
|---|---|---|---|
| Q1 | Neck bead OD (the segmented ring below the vertical ribs, the widest part) | yes | 20.8 |
| Q2 | From the very top of the neck (top of the small raised ring) down to the underside of the bead | yes | estimate 7.0 accepted |
| Q3 | Inner diameter of the neck opening at the top | yes | 8.8 |
| Q4 | From the very top of the neck down to the top of the shoulder lug | yes | estimate 9.4 accepted |
| Q5 | Was the 18.6 reading taken on the plain band at the top of the neck? | no | yes |

6. **A6:** D4 and D6 are photo estimates the user accepted. If the cap does not
   click on, or sits loose, measure D4 and reprint the base: it is the only number
   that moves the snap lip.
7. **A7:** the hinge clips on rather than printing in place. The base prints upside
   down, so a lid printed in place would be under the bed.
8. **A8:** hinge and latch sizes are defaults. If the latch is too tight or too loose,
   only D38 needs to change.
