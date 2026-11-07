## Part notes: bathroom-plate

**Strength for the least material: override the "Walls", "Top / bottom" and
"Infill" rows of the slicer settings above.** The plate works like an I-beam:
solid top and bottom skins carry the bending load, and a light core holds them
apart. A solid block would weigh 282 g for little extra stiffness.

| Setting (Bambu Studio) | Value | Why |
|---|---|---|
| Wall loops | **4** (about 1.7 mm) | strong edges where the clamps grip |
| Top shell layers | **6** (1.2 mm) | top skin: carries the load in compression |
| Bottom shell layers | **6** (1.2 mm) | bottom skin: carries it in tension |
| Sparse infill density | **20 %** | enough to hold up a 1.2 mm top skin cleanly |
| Sparse infill pattern | **Gyroid** | stiff in every direction, ties the two skins together |
| Top surface pattern | Monotonic line | smooth shelf face |

- Expect about **130 g of PETG**. Going to 15 % saves only about 9 g and the
  top skin starts to sag between infill lines; above 30 % adds weight for
  little gain.
- Optional, for the clamp zones: in Bambu Studio add a box modifier (about
  45 x 30 mm) over each bracket position (along each wall edge, 110 to 160 mm
  from the corner) with 40 % infill, so the clamp pads press on firmer
  material. Not needed if you tighten the screws snug only.

**Bed and warping.** A 170 x 170 PETG plate pulls on its corners as it
cools.
- Textured PEI plate, cleaned with dish soap and water first (no fingerprints).
- Bed 75–80 °C; keep the room draft-free (close the window / door, no fan on it).
- Add a **5 mm brim** if your corners have ever lifted with PETG. The part
  already uses the full 170 of the 180 bed, so keep the brim at 5 mm or less.
  Peel it off and deburr the bottom edge with a blade.
- Place it centred on the plate. Nothing else on the plate.

**Fitting.**
1. Loosen the clamp screws on both brackets.
2. Hold the plate level, rounded R40 corner towards you, the two straight
   edges towards the walls. Slide it diagonally into the corner so both edges
   enter both clamps.
3. Tighten the clamp screws evenly, snug only: PETG creeps under a hard
   point load, so do not crank them like on glass. The plate is 7.8 thick
   (glass 7.9), so a little more screw travel is normal.
4. Re-check the screws after a week of use.

**Load.** Toiletries, bottles and soap are fine. Keep heavy loads (more than
about 3 kg) near the walls and the brackets, not on the front corner. PETG takes
shower water and heat up to about 70 °C, but not boiling water.

**Accepted printcheck warnings:** none.
