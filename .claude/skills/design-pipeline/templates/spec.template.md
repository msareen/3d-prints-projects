# <project>: design specification

> Status: **draft**, revision 1. All dimensions in mm. Machine-readable twin:
> `spec.json` (same IDs). The model is built only from what is written here.

## 1. Purpose and context

What the part does, where it lives, what it touches, what loads it carries.

## 2. Inputs reviewed

| File | Kind | What it shows / says | Usable for |
|---|---|---|---|

## 3. Coordinate system and datum

- Origin:
- X:
- Y:
- Z: up, print direction; the part sits on Z = 0.
- Front of the part faces -Y (this is the front elevation).

## 4. Overall description

Plain-language description precise enough that someone could model the part
without seeing the inputs: main body, every feature, how they relate,
symmetry, edge treatment (fillets, chamfers).

## 5. Dimension register

| ID | Dimension | Value | Tol | Basis | Confidence | Critical | Source | Model param |
|---|---|---|---|---|---|---|---|---|

Basis: `given` (written in the text), `measured` (callout on a drawing/photo or
user's caliper value), `derived` (computed from other IDs, formula shown),
`estimated` (scaled from an image), `default` (design choice, no input).

## 6. Features

| ID | Feature | Count | Position (from datum) | Dimensions | Notes |
|---|---|---|---|---|---|

## 7. Consistency checks

Chains that must add up, symmetry, envelope; each with the arithmetic shown.

## 8. Print setup

Printer bed, nozzle, layer, material, supports, orientation (which face on the
bed and why), quantity, fits.

## 9. Assumptions

Numbered; each says what would change if it is wrong.

## 10. Open questions

| ID | Question | Blocking | Answer |
|---|---|---|---|
