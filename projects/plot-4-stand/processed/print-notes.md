## Part notes: plot-4-stand (spare foot for the game board)

**Orientation:** floor on the bed, open side up, as exported. No supports.
The lips' undersides are 45° and print cleanly.

**Brim:** none needed (2730 mm² on the bed). Keep the first layer clean: the
handle is narrow, and elephant foot is already hidden by the 0.4 bottom chamfer.

**Fit on the board (the clip):**
- The board's side rail end (12.8) pushes into the handle channel from the top,
  past the two lips. The lips are drawn 12.9 apart. FDM prints them about
  0.1 per side narrow, so they come out near the original's 12.7: a slight
  squeeze is the catch.
- Below the lips the channel is 15.2 wide (original 15.0).
- Test the fit before printing a second foot.
  - Too hard to push on, or a lip whitens or cracks: open the lips. Set
    `"press"` to 0.10 in `processed/fits-PLA.json` (+0.05 per side) and
    rebuild. Change it in 0.05 steps only.
  - Falls out: set `"press"` to 0.0 (−0.05 per side).
- PLA is much stiffer than the original's soft plastic. If the clip cracks
  even when opened, print it in PETG.

**Estimated sizes** (photo scale, not calipers): outer width 95.4, overall
length 69.5, rim height 10.0, wall and floor thicknesses, and lip depth 3.0.
They do not affect the fit except the lip depth. If the board sits too high
or too low in the channel, measure the original's lip depth and rebuild.

**Accepted printcheck warnings:** none.
