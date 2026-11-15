# Setup and usage

Back to the [README](../README.md).

## Setup

### Quick start

Clone, then run the init script from the repo root. It fetches the git
submodules (the 3d-print-design skill, at the commit this repo pins) and
creates the Python environment, then checks that the geometry stack imports.
It is safe to re-run, for example after a pull that moves the submodule.

```bash
git clone <this-repo-url>
cd 3d-prints-projects
./init.sh            # macOS, Linux, Git Bash
```

```powershell
.\init.ps1           # Windows PowerShell
# if script execution is blocked:
powershell -ExecutionPolicy Bypass -File .\init.ps1
```

The script runs steps 1 and 2 below for you. With uv it runs `uv sync`;
without uv it falls back to `pipeline.py setup`.

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
Linux. On Windows, point it at Chrome, or at Edge, which ships with Windows
and works the same:

```powershell
$env:CHROME_PATH = "C:\Program Files\Google\Chrome\Application\chrome.exe"
# or
$env:CHROME_PATH = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
```

Without either, it falls back to an SVG preview.

## Commands

Ask Claude something like *"new project from the photos in this folder: a
bracket for my shelf"*, or invoke `/3d-design-pipeline`. The commands it runs
(from the repo root):

```bash
uv run pipeline new <project>
uv run pipeline scrub <project>      # strip GPS / device info from input/ + output/printed-pic/ photos
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

## Showcase

[msareen.github.io/3d-prints-projects](https://msareen.github.io/3d-prints-projects/)
is a static site built from the committed projects. `showcase/build.py`
(standard library only) reads every project that has `output/release.json` and
writes `_site/`: the page (`showcase/index.html`, `showcase.js`, `showcase.css`,
`viewer.js`), a `projects.json` index, and copies of the files it shows:

- the brief, photos, sketches and drawings in `input/` (with the notes from
  `spec.json` `inputs` as captions);
- the 3D preview of the primary material's STLs (three.js r128 from cdnjs with
  an integrity hash), the `processed/drawings/preview*` renders and the drawing sheet;
- photos of the finished print from `output/printed-pic/` (the first one is the
  card picture);
- the downloads: each material's 3MF, STLs and print sheet, plus the drawing,
  the spec and `release.json`.

`build.py`, `spec.json` and the other working files are not published. Only files
tracked by git are included, so a local build shows what Pages will show, and
the build fails if any published photo still carries GPS. Preview it locally:

```bash
python showcase/build.py                 # --untracked to include files not committed yet
python -m http.server -d _site 8000      # http://127.0.0.1:8000/
```

`.github/workflows/showcase.yml` rebuilds and deploys it on every push to `main`
that touches `projects/` or `showcase/`. One-time setup: repository Settings ->
Pages -> Source: **GitHub Actions**.

## Skills

Skills live in `.claude/skills/`, where Claude Code discovers them
automatically as project skills.

| Skill | Path | Source |
|-------|------|--------|
| `3d-design-pipeline` | `.claude/skills/3d-design-pipeline` | this repo |
| `3d-print-design` | `.claude/skills/3d-print-design` | git submodule: my fork <https://github.com/msareen/3d-print-design-skill> (tracks `main`) of the original <https://github.com/Matteoikarieth96/3d-print-design-skill> |

### Updating the submodule skill

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

### Adding another skill

As a submodule (the repo must have a `SKILL.md` at its root):

```bash
git submodule add -b main <repo-url> .claude/skills/<skill-name>
```

Or as a plain folder `.claude/skills/<skill-name>/SKILL.md`. Add a row to the
table above.
