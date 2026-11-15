# 3d-prints-projects

This is by far the easiest and cheapest way I have found to go from a real
object to a 3D print: photograph the part (or the gap a part has to fill),
describe it, and let a coding agent turn that into a checked, printable model.
The repository was created with Claude Code, but its workflow and local skills
are also available to Codex and other agents that follow `AGENTS.md`. I have
used it to fill gaps around the house, to make parts for broken toys and to
copy things I already own, and it has worked every time.

It works because of **engineering drawing**. A part described by its
orthographic views (front, side and top elevations plus a plan section, with
every size dimensioned from one datum) is fully defined, and almost anything
can be built and printed from it. The engineering drawing course I did with
Claude is what made this click, and it is the idea the whole repo is built on.
The agent reads my photos and notes and writes the part down as a dimension
register. It asks me only for the measurements it cannot get from them. Then it
checks the finished model against drawings of itself.

From my side it is three steps:

1. **Take pictures.** Put a ruler or a cutting mat in the shot and add any
   measurements I have.
2. **Get a render.** First a written spec to confirm, then drawings and a 3D
   view to approve.
3. **Get the final output.** Checked STL and 3MF files for each material (PLA,
   PETG), ready to slice.

The modelling engine is **[3d-print-design](https://github.com/Matteoikarieth96/3d-print-design-skill)
by [Matteoikarieth96](https://github.com/Matteoikarieth96)** (MIT licence).
**3d-design-pipeline** is my own pipeline, which wraps it: it adds the spec
stage, the checked drawings, multi-material releases and multi-plate Bambu
Studio 3MFs on top. See [Credits](#credits).

## Showcase

**[See everything built so far in the project showcase](https://msareen.github.io/3d-prints-projects/)**:
what each part started from, a 3D preview, photos and GIFs of the print and the
files to download. It is rebuilt from `projects/` on every push to `main`
([how it works](docs/usage.md#showcase)).

## Getting started

1. Open this repository in your coding agent and create the project. The agent
   should follow `AGENTS.md`; Codex-compatible agents can discover the skills
   under `.agents/skills/`, while `.claude/skills/` remains for Claude Code.
   Either ask in plain words, or run the command yourself:

   ```bash
   > new project "<projectName>"
   # or, outside Claude:  uv run pipeline new <projectName>
   ```

   This creates `projects/<projectName>/` with `input/`, `processed/` and
   `output/` (with an empty `output/printed-pic/` for photos of the print).

2. Put your pictures (and any sketches or measurements) into `input/`, then
   scrub them. It strips GPS, timestamps and device info, and the checks fail
   until every photo is clean:

   ```bash
   cp ~/Pictures/*.jpg projects/<projectName>/input/
   uv run pipeline scrub <projectName>
   ```

3. Tell the agent what you want to make. It reads the inputs, asks for any
   missing measurement, and writes the spec (`spec.md` + `spec.json`). Check
   it and say yes: nothing is modelled before you confirm.

4. It builds the model and writes the drawings, the render and the STL preview
   into `processed/`. Look at them and ask for changes until you are happy.
   You can also run the steps yourself:

   ```bash
   uv run pipeline build <projectName>   # model + printcheck
   uv run pipeline draw <projectName>    # elevations + plan, checked vs the spec
   uv run pipeline view <projectName>    # 3D viewer on http://127.0.0.1:<port>/
   ```

   The drawings are in `processed/drawings/` (open `sheet.svg`).

5. When you are happy, ask it to **generate the output**:

   ```bash
   uv run pipeline finalize <projectName>
   ```

   This releases checked STL and 3MF files, a print sheet and the drawing in
   `output/`, one folder per material (`output/PETG/`, `output/PLA/`). Each
   material gets its own sizing (clearances for snap and press fits) and
   slicer settings. `--material PETG` releases just one.

Slicing and printing stay with you: it never contacts a printer.

6. Once it is printed, put a photo or two of the part into
   `output/printed-pic/` and scrub them the same way. The
   [showcase](https://msareen.github.io/3d-prints-projects/) uses the one named
   `cover*` (else the first) as the project's picture once you commit and push.

First time on this machine? Clone, then run the init script from the repo
root. It fetches the git submodule and creates the Python environment:

```bash
git clone <this-repo-url>
cd 3d-prints-projects
./init.sh            # macOS, Linux, Git Bash
```

```powershell
.\init.ps1           # Windows PowerShell
```

Details, optional Bambu Studio and Windows PNG previews are in
[Setup](docs/usage.md#setup).

## Use it in your own repo

To bring the pipeline into another repository, clone this one and run the
installer with the target folder (it can be an existing repo or a new folder):

```bash
git clone <this-repo-url>
python install.py /path/to/your-repo                # add --showcase for the GitHub Pages site
cd /path/to/your-repo
uv sync
uv run pipeline new <projectName>
```

It copies the pipeline to `.claude/skills/3d-design-pipeline/`, adds the
agent entry points in `.agents/skills/`, adds `3d-print-design` as a git
submodule (a plain clone if the target is not a git repo), appends the workflow
rules to `AGENTS.md`, and adds a `pyproject.toml` and the `.gitignore` lines.
It never overwrites an existing file unless you pass `--force`, never commits,
and `--dry-run` shows what it would do. It needs Python 3.11+, git and
[uv](https://docs.astral.sh/uv/).

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
- **3d-design-pipeline** is my own workflow. Its authoritative implementation
  is in `.claude/skills/3d-design-pipeline/` for Claude Code compatibility,
  with agent-neutral discovery entries in `.agents/skills/`. The projects in
  `projects/` were created with Claude Code but are designed to be worked on by
  any agent that follows `AGENTS.md`.

## License

This repository is licensed under the [MIT License](LICENSE). The
`3d-print-design` git submodule is separately licensed under MIT by its
upstream author; see its included license for its terms and copyright notice.

## Documentation

| Page | What is in it |
|---|---|
| [How the pipeline works](docs/pipeline.md) | The stages and their gates, the pipeline diagram, which skill does what, what the pipeline adds, the project folder layout, and how photos are scrubbed of GPS and device info |
| [Setup and usage](docs/usage.md) | Clone and Python environment, Bambu Studio and PNG previews on Windows, every `pipeline` command, the two skills and how to update or add one |
| [Projects](docs/projects.md) | Every design in this repo, and the hair band as a worked example |
| [Showcase](docs/usage.md#showcase) | The GitHub Pages site built from `projects/`: how it is generated, previewed locally and published |
