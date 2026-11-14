## Print in place, upright

- **Orientation:** upright as exported, standing on the plate's bottom edge, with the rack pins pointing sideways. Both lids print closed on their hinges, so there is nothing to fit afterwards.
- **Lower lid:** it stands on the bed.
- **Upper lid:** it needs **support under it**. Use tree support, or a support enforcer painted on its underside. The support stands on top of the lower lid, about 24 mm tall, under the lid's U only.
- **Before printing:** check the slicer preview. There must be no support inside the 0.4 mm hinge gaps or the 0.3 mm latch gap. If your slicer puts some there, add a support blocker around the hinge (the left end of each loop).
- **Upper loop base:** the 45 deg wings under it are part of the design. It needs no support.
- **After printing:** remove the support, then open each lid once by pulling its right end forward. That breaks any light fusing in the gaps.

## Using it

- **Open:** pull the right end of the lid forward. It swings about 105 deg along the cable.
- **Close:** press it shut. The hook on the lid's thin right skirt clicks past the 45 deg bead on the latch post, as on seba-med-cap's flip lid.

## Test fit, then adjust in 0.05 mm steps

- **Hinge:** cone clearance `CONE_GAP` is 0.25, one step tighter than rev 4 (user: tighter). If it fuses or is stiff, go to 0.30. If it wobbles, go to 0.20. The lid has about 0.35 mm axial play before the cones take it.
- **Latch** (after seba-med-cap): the bead `BEAD_H` is 1.05 (rev 9: raised 0.30 from 0.75 at your request, not the usual 0.05 step), so the hook travels 0.75 mm over it on a 1.0 mm arm (`SKIRT_T`).
  - The arm now bends to about 4.6 % strain, above the usual ~3 % guide for PLA. Open and close it gently the first few times.
  - If the skirt cracks or stays bent outwards, go back towards 0.90.

## Motion check (manifold3d sweep, both loops)

- **Closed:** no overlap.
- **1-3 deg:** the hook rides 0.73 mm over the bead. This is the click, and it holds the lid shut.
- **4-105 deg:** free.
- **About 110 deg:** the lid stops against the base.
- **Lid moved 0.35 mm up or down:** no contact. The cone pins hold it on the hinge.

## Accepted printcheck warnings

- **on_bed:** the upper lid is off the bed. It is captured on its hinge (it cannot drop) and is printed on support.
- **overhang:** the upper lid's underside, about 240 mm2, sits on support.
- **thin_walls:** the 45 deg tips of the bead and the hook.
