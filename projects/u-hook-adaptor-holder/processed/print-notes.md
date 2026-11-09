## Part notes: u-hook-adaptor-holder (Surface 65 W brick holder) + pin test sample

**Plate:** the 3MF holds two objects standing upright: the holder (blue) and, to its right, the pin test sample (orange). Print the **sample first, on its own**: delete or disable the holder object in the slicer.

**Pin test sample: quick print settings** (it only checks the fit):
- Layer: keep **0.2 mm** so the pins come out the same as on the holder.
- 2 walls, 3 top / 3 bottom layers, **5-10 % infill** (lightning or grid).
- Speed: the slicer's fast or draft speeds are fine for the plate. Keep the outer wall at 40-60 mm/s so the 1.7 mm groove stays true.
- No brim, and no supports.
- It is 20 × 23 × 54 mm, and takes about 10-15 minutes.

**Test the fit:**
1. Push both heads into two neighbouring big round keyholes, flat plate against the steel, then press down. The grooves should ride down the narrow slots and the sample should hang on its own, snug against the steel.
2. Heads will not go in: the 9.6 mm head is too big for the round hole. I step it back towards 9.0 or 8.6.
3. It goes in but will not slide down: the 5.6 mm groove is too wide for the slot, or the 1.7 mm groove is too narrow for the 1.6 mm steel. I change either in 0.05 mm steps.
4. It slides down but wobbles a lot or drops out: the groove is too loose. I tighten it in 0.05 mm steps.
5. If it hangs snug, print the holder. Its pins are identical.

**Holder: normal settings** (the print sheet's PLA settings): 4 walls, 30 % gyroid, 0.2 mm. The pins carry the brick, so do not use the sample's low-infill settings here.

**Rev 2 pins:** the head is now 9.6 mm across (was 7.6) and both groove and head are point-down teardrops. The groove is unchanged: 5.6 mm across and 1.7 mm wide, which the rev 1 sample proved. No supports are needed, and printcheck gives no warnings. Re-print the sample first: it checks that the bigger head still enters the round holes.

**Hanging the holder:** heads into the two round holes, then push down about 10 mm. Lower the brick in from the top: its AC input faces up, and its DC cable and USB-A plug go down through the open bottom.

**Heat:** PLA softens at about 55 °C. The brick runs at 40-50 °C and the mesh keeps air moving, so do not cover it or wrap the cable around it.
