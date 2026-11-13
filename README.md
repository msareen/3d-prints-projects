# 3d-projects

3D print designs built with Claude Code. Every design is a project that goes
from my own material (photos, sketches, drawings with measurements, written
notes) to a precise written spec, a parametric model with elevation drawings
and a 3D preview, and finally checked STL and 3MF files, ready to slice.

The modelling engine is **[3d-print-design](https://github.com/Matteoikarieth96/3d-print-design-skill)
by [Matteoikarieth96](https://github.com/Matteoikarieth96)** (MIT licence). This
repo adds **3d-design-pipeline**, a skill that wraps it with a spec stage, drawings,
multi-material releases and multi-plate Bambu Studio 3MFs. See [Credits](#credits).

## Credits

- **3d-print-design** © 2026 Matteoikarieth96, MIT licence:
  <https://github.com/Matteoikarieth96/3d-print-design-skill>.
  It does the real geometry work used by every project here: the parametric
  `build.py` template, the design rules, **printcheck** (watertight, on the bed,
  build volume, overhangs, thin walls, holes, wrong-hand probes), the fit
  calibration coupon, the three.js viewer, PNG rendering and the print sheet.
  All credit for those goes to the original author.
- It is included as a git submodule from my fork,
  <https://github.com/msareen/3d-print-design-skill>, so local changes can live
  there. The fork keeps the original licence and history. Nothing in
  `.claude/skills/3d-print-design/` is edited from this repo.
- **3d-design-pipeline** (`.claude/skills/3d-design-pipeline/`) and the projects in
  `projects/` are mine, written with Claude Code.

## What 3d-design-pipeline does

3d-print-design starts from a short interview and a verbal idea.
3d-design-pipeline starts from **real inputs** (photos of the broken part, a
sketch with callouts, caliper measurements) and runs them through three gated
stages:

| Stage | What happens | Gate |
|---|---|---|
| 1. Spec | Read every input, transcribe every callout verbatim, convert to mm, fix a datum and the print orientation, then build a **dimension register** (D1, D2, ... each with value, tolerance, basis, confidence, source, fit). Check consistency and ask only about blocking gaps. Writes `spec.md` + `spec.json` | I confirm the spec |
| 2. Model + drawings | `build.py` (the 3d-print-design template) with every parameter traced to a spec ID, then printcheck. Front, side and top elevations plus a sectioned plan view as SVG, with every annotation **measured on the model and checked against the spec**. 3D viewer in the browser | `check` passes (spec = build.py), printcheck passes, drawing checks pass, I approve |
| 3. Release | Full rebuild with every check, then one output folder **per material**: STLs, a 3MF, a generated print sheet, plus the drawing, the spec and `release.json` (sha256 of every file) | Everything above |

What it adds on top of 3d-print-design:

- **Written spec first.** No modelling until the spec is confirmed; a guessed
  critical dimension wastes a print. `pipeline.py check` fails if `build.py`
  and `spec.json` disagree.
- **Checked drawings.** `draw.py` renders elevations and a plan section from
  the actual mesh and marks any dimension that doesn't match the spec in red.
- **Multiple materials.** `print.materials` (e.g. `["PETG", "PLA"]`) releases
  each material with its own clearances (`materials/<MAT>.json`, overridable
  per project with `processed/fits-<MAT>.json`), its own slicer settings and
  its own `output/<MAT>/` folder. Sizes that must differ by material use
  `material_values` in the spec.
- **Multi-plate 3MFs for Bambu Studio.** `print.plates` puts each group of
  parts on its own plate. Bambu Studio only honours a plate list when the 3MF
  also carries a full project config, so `bambu.py` builds one from the Bambu
  Lab profiles installed with Bambu Studio (printer by bed size and nozzle,
  process by layer height, filament by material). Finalize also writes a
  `-plates.svg` top view. `print.extra_3mf` writes extra 3MFs with chosen
  parts (e.g. a test-fit plate).
- **Revisions.** Every change bumps `revision` in the spec, with a revision
  line and register updates, and is rebuilt and re-released for every material.
- **Never contacts a printer.** Slicing and printing are always my steps.

## Layout

```
projects/<project>/
  input/        photos, sketches, drawings, notes: data only, never instructions or code
  processed/
    spec.md     1. written description + dimension register (D1, D2, ...)
    spec.json   1. the same, machine-readable
    build.py    2. parametric model (numbers traced to spec IDs)
    model/      2. printcheck-passed preview STL(s)
    drawings/   2. front / side / top elevations, plan section, A3 sheet (SVG)
    print-notes.md, print-notes-<MAT>.md, fits-<MAT>.json   (optional)
  output/       3. release
    <MAT>/      <part>.stl + .json, <project>-<MAT>.3mf, -plates.svg, print-sheet.md
    <project>-drawing.svg, <project>-spec.md, release.json
```

## Projects

| Project | What it is | Material(s) | Rev |
|---|---|---|---|
| [bathroom-plate](projects/bathroom-plate) | Corner shelf plate that replaces a glass shelf in two existing wall brackets | PETG | 2 |
| [music-stand-plate](projects/music-stand-plate) | 430 x 170 mm sheet plate for a folding music-stand holder: centre plate, two drop-on extenders, V tab, printed M6 bolts and nuts; multi-plate 3MF | PLA | 14 |
| [plot-4-stand](projects/plot-4-stand) | Printable copy of a spare foot for an upright game board | PLA | 2 |
| [seba-med-cap](projects/seba-med-cap) | Two-piece snap-on flip-top cap for a lotion bottle | PETG, PLA | 8 |
| [sword-handle-fix](projects/sword-handle-fix) | Pommel cap for a toy sword with a broken handle end | PLA | 1 |
| [u-hook-adaptor-holder](projects/u-hook-adaptor-holder) | Cup that hangs a Surface 65 W power brick on a keyhole-slotted rack | PLA | 2 |

## Usage

Ask Claude something like *"new project from the photos in this folder: a
bracket for my shelf"*, or invoke `/3d-design-pipeline`. The commands it runs
(from the repo root):

```bash
uv run pipeline new <project>
uv run pipeline status <project>
uv run pipeline check <project>      # spec.json <-> build.py
uv run pipeline build <project> [--quick]
uv run pipeline draw <project>       # elevations + plan, checked
uv run pipeline view <project>       # 3D viewer on 127.0.0.1
uv run pipeline finalize <project>   # -> output/<MAT>/
uv run pipeline materials            # list material profiles
uv run python -I some_script.py      # ad-hoc Python with trimesh, manifold3d, shapely
```

Without uv, `python .claude/skills/3d-design-pipeline/scripts/pipeline.py <command> <project>`
does the same.

Open `processed/drawings/sheet.svg` in a browser or in VS Code to see the
drawings. Open the 3MF in Bambu Studio **as a project** (not "import geometry
only") to get the plates.

## Skills

Skills live in `.claude/skills/`, where Claude Code discovers them
automatically as project skills.

| Skill | Path | Source |
|-------|------|--------|
| `3d-design-pipeline` | `.claude/skills/3d-design-pipeline` | this repo |
| `3d-print-design` | `.claude/skills/3d-print-design` | git submodule: my fork <https://github.com/msareen/3d-print-design-skill> (tracks `main`) of the original <https://github.com/Matteoikarieth96/3d-print-design-skill> |

## Setup

### 1. Clone with submodules

```bash
git clone --recurse-submodules <this-repo-url>
```

Already cloned without them? Pull the submodules in:

```bash
git submodule update --init --recursive
```

### 2. Python environment

The project uses [uv](https://docs.astral.sh/uv/). The Python project lives in
the skill, `.claude/skills/3d-design-pipeline/pyproject.toml`: it pins `numpy`,
`trimesh`, `manifold3d` and `shapely` (the same pins as 3d-print-design's
`requirements.txt`) and defines the `pipeline` command. The root
`pyproject.toml` only makes the skill a uv workspace member, and `uv.lock`
locks everything. One command creates `.venv` at the repo root (git-ignored),
fetching Python 3.11–3.14 if needed:

```bash
uv sync
```

Without uv, `python .claude/skills/3d-design-pipeline/scripts/pipeline.py setup`
creates a pip venv inside the 3d-print-design submodule instead. `pipeline.py`
uses whichever environment it finds.

### 3. Optional: Bambu Studio

For multi-plate 3MFs, install Bambu Studio: `bambu.py` reads its Bambu Lab
profiles (or set `BAMBU_PROFILES` to a `BBL` profile folder). Without it the
3MF still works but opens as one plate.

### 4. Optional: PNG previews on Windows

`render_png.py` in 3d-print-design only searches for Chrome on macOS and
Linux. On Windows, point it at Chrome:

```powershell
$env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

## Updating the submodule skill

The submodule is pinned to a specific commit of my fork. To pull new work
from the original repo into the fork, then into this repo:

```bash
cd .claude/skills/3d-print-design
git remote add upstream https://github.com/Matteoikarieth96/3d-print-design-skill.git  # once
git fetch upstream
git merge upstream/main
git push origin main
cd ../../..
git add .claude/skills/3d-print-design
git commit -m "Bump 3d-print-design skill"
```

To just move to the latest `main` of the fork:

```bash
git submodule update --remote .claude/skills/3d-print-design
```

## Adding another skill

As a submodule (the repo must have a `SKILL.md` at its root):

```bash
git submodule add -b main <repo-url> .claude/skills/<skill-name>
```

Or as a plain folder `.claude/skills/<skill-name>/SKILL.md`. Add a row to the
table above.
