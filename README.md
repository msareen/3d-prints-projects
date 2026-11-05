# 3d-projects

3D print designs built with Claude Code and agents. Every design is a project
that goes from the user's material (photos, sketches, drawings with
measurements, written notes) to a precise written spec, a parametric model
with elevation drawings and a 3D preview, and finally checked STL and 3MF
files.

## Pipeline

```
projects/<project>/
  input/        photos, sketches, drawings, notes, PDFs: anything describing the part
  processed/
    spec.md     1. precise written description + dimension register (D1, D2, ...)
    spec.json   1. the same, machine-readable
    build.py    2. parametric model (numbers traced to spec IDs)
    model/      2. printcheck-passed preview STL(s)
    drawings/   2. front / side / top elevations, plan section, A3 sheet (SVG)
  output/       3. <part>.stl, <project>.3mf, drawing, spec, print sheet, release.json
```

| Stage | What happens | Gate |
|---|---|---|
| 1. Spec | Read every input, transcribe every callout, convert to mm, fix a datum, build the dimension register (value, tolerance, basis, confidence, source), check consistency, and ask about gaps | The user confirms the spec |
| 2. Model + drawings | `build.py` from the spec, then printcheck, then elevations and plan view; drawing annotations are checked against the model; 3D viewer in the browser | printcheck passes, drawing checks pass, the user approves |
| 3. Release | Full rebuild with every check, then STL + 3MF (parts centred on the bed) + drawing + spec into `output/` | Everything above |

Ask Claude something like *"new project from the photos in this folder: a
bracket for my shelf"*, or invoke `/design-pipeline`. The commands it runs
(from the repo root):

```bash
python .claude/skills/design-pipeline/scripts/pipeline.py new <project>
python .claude/skills/design-pipeline/scripts/pipeline.py status <project>
python .claude/skills/design-pipeline/scripts/pipeline.py check <project>      # spec.json <-> build.py
python .claude/skills/design-pipeline/scripts/pipeline.py build <project> [--quick]
python .claude/skills/design-pipeline/scripts/pipeline.py draw <project>       # elevations + plan, checked
python .claude/skills/design-pipeline/scripts/pipeline.py view <project>       # 3D viewer on 127.0.0.1
python .claude/skills/design-pipeline/scripts/pipeline.py finalize <project>   # -> output/
```

Open `processed/drawings/sheet.svg` in a browser or in VS Code to see the drawings.

## Skills

Skills live in `.claude/skills/`, where Claude Code discovers them
automatically as project skills.

| Skill | Path | Source |
|-------|------|--------|
| `design-pipeline` | `.claude/skills/design-pipeline` | this repo |
| `3d-print-design` | `.claude/skills/3d-print-design` | git submodule: https://github.com/Matteoikarieth96/3d-print-design-skill (tracks `main`) |

`design-pipeline` adds stages 1 and 2, the drawings, the spec checks and the
3MF export. For modelling, printcheck, the viewer and the print sheet it uses
`3d-print-design`.

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

You need Python 3.11–3.14. One command creates the geometry venv inside the
3d-print-design submodule (where it is git-ignored) and installs `numpy`,
`trimesh`, `manifold3d` and `shapely`:

```bash
python .claude/skills/design-pipeline/scripts/pipeline.py setup
```

> The 3d-print-design docs refer to `.venv/bin/python`; on Windows the
> interpreter is `.venv/Scripts/python.exe`. `pipeline.py` handles both.

### 3. Optional: PNG previews on Windows

`render_png.py` in 3d-print-design only searches for Chrome on macOS and
Linux. On Windows, point it at Chrome:

```powershell
$env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

## Updating the submodule skill

The submodule is pinned to a specific commit. To move to the latest `main`:

```bash
git submodule update --remote .claude/skills/3d-print-design
git add .claude/skills/3d-print-design
git commit -m "Bump 3d-print-design skill"
```

## Adding another skill

As a submodule (the repo must have a `SKILL.md` at its root):

```bash
git submodule add -b main <repo-url> .claude/skills/<skill-name>
```

Or as a plain folder `.claude/skills/<skill-name>/SKILL.md`. Add a row to the
table above.
