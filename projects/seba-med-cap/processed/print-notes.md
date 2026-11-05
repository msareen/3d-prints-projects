**Accepted printcheck warnings**
- **layer_alignment:** the slot floor (5.7), sleeve rim (10.7) and lid clip top (5.05) sit 0.05–0.1 off a layer. The slicer rounds them.
- **small_holes:** the 2 mm gap between the hinge pin and the skirt is the clip's swing path, not a fastener hole.
- **thin_walls (base):** a few samples on the edges of the sleeve flex slots, where the 45° lip chamfer meets the slot wall. This is a sampling artifact, not a real wall.

**Printing**
- The groove around the 5 mm spout has a short 1.6 mm bridge as its roof. Let the slicer bridge it. No supports.
- Seam: rear, away from the latch (+X) and the hinge (−X).

**After printing**
1. Check that the hinge pin is free between the knuckles. Trim any strings.
2. Lay the lid open flat beside the base, with the clip mouth over the pin, and press the clip onto the pin.
3. Fold the lid over and press the tab. The plug, the seal ring and the latch click shut.
4. Push the base onto the bottle neck until it clicks over the bead.

**Test fit first**
- The snap height (D4, 7.0 mm from the neck top to the underside of the bead) is a photo estimate. If the base won't click on, or sits loose, measure D4 and reprint the base.
- If the latch is too stiff or too weak, change `LATCH_DEPTH` (D38) or `LATCH_PRELOAD` (D45). The values per material are in the print-notes for each material.
- If the lid is too tight to close, reduce the plug bulb `PLUG_BULB_D` (D51) by 0.1 first, then set `RING_FIT` (seal ring) to `FITS["sliding"]`.
- The plug bore (2.9) shows as a "small hole" warning. It is the hollow core that lets the plug flex, not a fastener hole.
- Rev 5: the skirt now reaches the shoulder (no gap). If it stops the cap clicking fully onto the bead, sand the rim, or lower `SKIRT_EXT` (D43, 8.0) by 0.2.
- Rev 5: the seal tube is 4 mm long and goes into the neck bore to stop the wobble. Push the cap on straight.

The seal stops splashes but won't hold pressure. Don't squeeze the bottle hard with the lid closed. Let the parts cool before you snap them together.
