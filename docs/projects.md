# Projects

Back to the [README](../README.md).

## All projects

| Project | What it is | Material(s) | Rev |
|---|---|---|---|
| [bathroom-plate](../projects/bathroom-plate) | Corner shelf plate that replaces a glass shelf in two existing wall brackets | PETG | 2 |
| [hair-band](../projects/hair-band) | Chain-link headband with two rows of grip teeth, copied from photos; hidden spine for stiffness, see-through gaps on the arms, prints flat without supports | PETG, PLA | 4 |
| [music-stand-plate](../projects/music-stand-plate) | 430 x 170 mm sheet plate for a folding music-stand holder: centre plate, two drop-on extenders, V tab, printed M6 bolts and nuts; multi-plate 3MF | PLA | 14 |
| [plot-4-stand](../projects/plot-4-stand) | Printable copy of a spare foot for an upright game board | PLA | 2 |
| [seba-med-cap](../projects/seba-med-cap) | Two-piece snap-on flip-top cap for a lotion bottle | PETG, PLA | 8 |
| [sword-handle-fix](../projects/sword-handle-fix) | Pommel cap for a toy sword with a broken handle end | PLA | 1 |
| [u-hook-adaptor-holder](../projects/u-hook-adaptor-holder) | Cup that hangs a Surface 65 W power brick on a keyhole-slotted rack | PLA | 2 |
| [u-hook-cable-manager](../projects/u-hook-cable-manager) | Cable manager for the same rack keyholes: two hinged U-strap cable loops, printed in place with snap latches | PLA | 9 |

## A design in practice: the hair band

[hair-band](../projects/hair-band) shows the loop better than any description.

- **Rev 1 (spec from photos).** Four phone photos of a moulded chain-link
  headband lying on a cutting mat. Claude fitted the mat's 1/2 inch grid to
  scale the top view (outline sizes ±3 mm). It transcribed the links and teeth
  from the side and close-up shots and asked about only four things: sizes,
  material, printer and tooth thickness.
- **Rev 3 (the look).** The first model was too square. The links became round
  oval wire loops, slanted 15° and twisted 10° so each passes in front of the
  next. To print them flat without supports, every wire got a hidden 50°
  keel underneath (a teardrop section).
- **Rev 4 (after printing it).** The print showed three problems, each fixed in
  the spec first and then in the model:
  - *The slicer supported the teeth.* A layer-by-layer check found the keel
    ridges under the teeth and the upper wires starting in mid-air. Now a
    hidden 2.6 mm spine on the inner face carries the upper wires, and every
    tooth grows out of it on a 50° web.
  - *Too flexible.* More infill would not have helped, because 2.4 mm wires
    are almost all perimeter walls. The spine fuses the links into one strip,
    roughly 3x stiffer.
  - *The tips poked the skin.* The ends are now smooth rounded pads.
  - *But keep some chain gaps.* The arms have no teeth, so the spine there has
    a see-through window behind each link. Each window is flat-topped (a short
    bridge, under 2/3 of the wall depth, so printcheck counts it as held at
    both ends) and slopes at 50° beyond that. The windows sit near the tips,
    where the bending load is small.

Each revision bumps the spec and re-runs `check`, printcheck and the drawing
checks before `finalize` releases PETG and PLA again.
