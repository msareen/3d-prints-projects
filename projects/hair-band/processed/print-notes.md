## Part notes: hair-band (rev 4)

**Supports: OFF.** Print it as the file comes: flat on the bed, the C shape lying down, with **supports switched off**. Rev 4 is built so nothing starts in mid-air. The upper wires rest on the hidden spine, and every tooth grows out of the spine on a 50° web. A layer-by-layer check finds no area that needs support. If your slicer still shows a "floating regions" or "needs support" warning, ignore it and leave supports off.

**Stiffness: walls matter more than infill.** The band is stiffer in rev 4 because of the hidden 2.6 mm spine along the inner face. More infill alone would not have done it: the 2.4 mm wires are almost all walls. For the stiffest band use **4 walls and 100 % infill** (rectilinear or gyroid; at 2.6 mm the spine still has a small infill core). 30 % infill makes it a little softer, not floppy. Still too soft? Print the PLA version (about 1.5x stiffer), or ask for a thicker spine (D32).

**Bed adhesion.** The spine, the flattened bottom wires, the tip pads and the lower teeth touch the bed (about 810 mm²). A **3 mm brim**, a clean bed and a slow first layer keep the arm ends down.

**Seam and speed.** Use the seam setting "aligned" or "back"; with "nearest" or "random" the round wires collect scars. Slow down the outer walls (about 40 mm/s) so the 1.4 mm teeth and the wire crossings stay clean.

**Tips.** Each end is now a smooth rounded pad (radius 2.2 mm) instead of the end of a wire loop. If the first layer leaves a sharp lip (elephant's foot) round a pad, rub it off with fine sandpaper; that is the edge that touches the skin behind the ear.

**Accepted printcheck warnings.**
- Thin walls: the thin samples (around z 4.9) are the sharp edge of the hidden 50° keel under the upper wires, on the outer side of the spine. A keel is meant to come to an edge; the slicer prints it as a single line.
- Small hole: one 0.3 mm sliver gap between a wire and the spine on the left arm. It is thinner than one extrusion line, so the slicer fills it.
- Layer alignment: a few short flat stretches of the sloped window floors fall between layers; the slicer rounds them.

**See-through windows (arms).** Behind each link on the arms there is a small window (about 3.9 x 1.9 mm) through the hidden spine. Its top is a short bridge, at most 2.7 mm, held on both sides. That prints cleanly with supports off; at worst the top edge sags a hair, invisible in black. If a stray string crosses a window, pick it out with a needle. The toothed part keeps a solid spine.

**Teeth.** The teeth are 1.4 mm round pins with a web underneath (a shark-fin shape seen from the side), all pointing straight at the head. If one has a stringy or rough tip, trim it with a knife or rub it on fine sandpaper so it glides through hair.

**Test fit.** The size comes from a photo of the original (±3 mm). Try it on before printing a second one:
- Too tight (it presses behind the ears): increase D1 (inside width, now 116) by 4 mm and rebuild. Rev 4 is stiffer, so it presses harder than rev 3 at the same size.
- Too loose (it slides off): decrease D1 by 4 mm.
- Best: measure the original's inside width with a ruler and use that number.

Open it gently over the head the first few times. PETG springs back; it does not need to be warmed.
