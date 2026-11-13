## Print in place: one piece, lids already on their hinges

- **Orientation:** lay it on its back as exported. The two rack pin heads touch the bed, and the lids are on top, closed. Do not rotate it.
- **Supports: on build plate only.** They fill the 4.75 mm under the plate's back and the loop bases. Do not use "everywhere": that would fill the 0.3 mm hinge and latch gaps and weld the lids shut.
- **Lid ceilings:** they bridge about 28 mm over the cable space, as in the reference. Keep bridge cooling on.
- **After printing:** peel the support off the back. Then open each lid once by pulling its right end, with the latch side, away from the base. The first opening breaks any light fusing in the 0.3 mm gaps.

## Using it

- **Open:** pull the right end of the lid forward. The skirt flexes and the barb leaves the notch. The lid swings open about 105 deg along the cable.
- **Close:** press the lid shut until the barb clicks under the post notch.
- **Hang:** push both rack pin heads into the round holes of the keyholes, then let it drop so the grooves slide down the slots, as with the adaptor holder.

## Test fit, then adjust in 0.05 mm steps

These are first guesses for PLA, checked only by the motion sweep. FDM adds about 0.1 mm per side, so gaps print smaller than drawn.

- **Hinge or lid fused or stiff:** raise `GAP` 0.30 -> 0.35 -> 0.40. This changes every clearance: hinge, posts and latch.
- **Latch too stiff:** lower `BARB` 0.50 -> 0.45, or thin `SKIRT_T` 1.3 -> 1.2.
- **Latch too loose:** raise `BARB` to 0.55.

## Motion check (manifold3d sweep, both loops)

- **Closed:** no overlap.
- **0-4 deg:** the barb rides 0.2 mm over the post. That is the click.
- **6-105 deg:** free.
- **About 110 deg:** the lid stops against the base.
- The cone pins never touch their sockets.

## Accepted printcheck warnings

- **on_bed:** the two lids do not touch the bed. They rest 0.30 mm above the base, as in a print-in-place hinge, and build.py checks every lowest face of each lid for this.
- **overhang:** the plate's back sits over the build-plate support, and the lid ceilings are bridges.
- **thin_walls:** the barb's 45 deg tip.
- **layer_alignment:** the 0.3 gaps and the hinge axis levels are not on the 0.2 grid. The slicer rounds them, so check that the gaps stay open in the slicer preview.
