#!/usr/bin/env python3
"""pipeline.py: drive a 3d-design-pipeline project from input to STL + 3MF (stdlib only).

    python pipeline.py setup                  create the geometry environment (`uv sync` if uv is
                                              installed, else a pip venv in 3d-print-design/.venv)

With uv, every command is also `uv run pipeline <command> ...` (see pyproject.toml).
    python pipeline.py new <project>          scaffold projects/<project>/{input,processed,output}
    python pipeline.py status <project>       what exists, what is next
    python pipeline.py check <project>        validate spec.json and its links to build.py
    python pipeline.py build <project>        run processed/build.py -> processed/model/ (printcheck gated)
    python pipeline.py draw <project>         elevations + plan -> processed/drawings/ (checked vs spec)
    python pipeline.py view <project>         3D viewer for processed/model/ on 127.0.0.1 (Ctrl+C stops)
    python pipeline.py finalize <project>     check + full build + draw, then output/<MATERIAL>/ (STL, 3MF,
                                              print sheet) for each spec print.materials, + drawing, spec
    python pipeline.py materials              list the material profiles (materials/*.json)

Projects live in $DESIGN_PROJECTS_DIR, else <repo>/projects when this skill sits
in <repo>/.claude/skills/, else ./projects. The 3d-print-design skill is found
via $PRINT3D_SKILL_DIR, else as a sibling skill folder, else ~/.claude/skills.
"""
from __future__ import annotations

import argparse
import ast
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
BASIS = {"measured", "derived", "default", "estimated", "given"}
CONFIDENCE = {"high", "medium", "low"}
STATUS = {"draft", "confirmed"}


# --------------------------------------------------------------------------
# locations
# --------------------------------------------------------------------------
def projects_root() -> Path:
    env = os.environ.get("DESIGN_PROJECTS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    if SKILL_DIR.parent.name == "skills" and SKILL_DIR.parent.parent.name == ".claude":
        return SKILL_DIR.parent.parent.parent / "projects"
    return Path.cwd() / "projects"


def print3d_dir() -> Path:
    cands = []
    if os.environ.get("PRINT3D_SKILL_DIR"):
        cands.append(Path(os.environ["PRINT3D_SKILL_DIR"]).expanduser())
    cands += [SKILL_DIR.parent / "3d-print-design", Path.home() / ".claude" / "skills" / "3d-print-design"]
    for c in cands:
        if (c / "scripts" / "cad.py").is_file():
            return c.resolve()
    sys.exit("cannot find the 3d-print-design skill: run `git submodule update --init` or set PRINT3D_SKILL_DIR")


GEOMETRY_MODULES = ("numpy", "trimesh", "manifold3d", "shapely")


def _has_geometry_stack() -> bool:
    import importlib.util
    return all(importlib.util.find_spec(m) for m in GEOMETRY_MODULES)


def venv_python(required: bool = True) -> Path | None:
    """The interpreter for the geometry scripts, in this order:
    1. the one running this script, if it has the geometry stack (`uv run pipeline ...`);
    2. the uv environment: <repo>/.venv (uv workspace) or this skill's own .venv;
    3. the older pip venv in the 3d-print-design submodule (3d-print-design/.venv)."""
    if _has_geometry_stack():
        return Path(sys.executable)
    bases = []
    if SKILL_DIR.parent.name == "skills" and SKILL_DIR.parent.parent.name == ".claude":
        bases.append(SKILL_DIR.parent.parent.parent / ".venv")
    bases += [SKILL_DIR / ".venv", print3d_dir() / ".venv"]
    for base in bases:
        for p in (base / "Scripts" / "python.exe", base / "bin" / "python"):
            if p.is_file():
                return p
    if required:
        sys.exit("geometry environment missing: run `uv sync` (or `python pipeline.py setup`) first")
    return None


def project_dir(name: str, must_exist: bool = True) -> Path:
    if not NAME_RE.fullmatch(name or ""):
        sys.exit(f"invalid project name {name!r}: lowercase letters, digits and dashes, max 64")
    p = projects_root() / name
    if must_exist and not p.is_dir():
        sys.exit(f"no such project: {p} (create it with `pipeline.py new {name}`)")
    return p


def run(cmd, cwd=None, env=None) -> int:
    print("$ " + " ".join(str(c) for c in cmd), flush=True)
    return subprocess.call([str(c) for c in cmd], cwd=str(cwd) if cwd else None, env=env)


# --------------------------------------------------------------------------
# commands
# --------------------------------------------------------------------------
def cmd_setup(args) -> int:
    uv = shutil.which("uv")
    if uv:
        # pyproject.toml in this skill pins the geometry stack; uv.lock pins everything else
        rc = run([uv, "sync"], cwd=SKILL_DIR)
        if rc == 0:
            rc = run([uv, "run", "python", "-c",
                      "import trimesh, manifold3d, shapely, numpy; print('geometry stack ok')"], cwd=SKILL_DIR)
        return rc
    p3 = print3d_dir()
    if venv_python(required=False):
        print(f"venv already present: {venv_python()}")
    else:
        rc = run([sys.executable, "-m", "venv", p3 / ".venv"])
        if rc:
            return rc
    py = venv_python()
    rc = run([py, "-m", "pip", "install", "-q", "-r", p3 / "requirements.txt"])
    if rc == 0:
        run([py, "-c", "import trimesh, manifold3d, shapely, numpy; print('geometry stack ok')"])
    return rc


def cmd_new(args) -> int:
    proj = project_dir(args.project, must_exist=False)
    if proj.exists() and any(proj.iterdir()):
        print(f"{proj} already exists and is not empty; nothing changed", file=sys.stderr)
        return 1
    for sub in ("input", "processed", "output"):
        (proj / sub).mkdir(parents=True, exist_ok=True)
        (proj / sub / ".gitkeep").touch()
    tpl = SKILL_DIR / "templates"
    spec = json.loads((tpl / "spec.template.json").read_text(encoding="utf-8"))
    spec["project"] = args.project
    spec["parts"][0]["name"] = args.project
    (proj / "processed" / "spec.json").write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    md = (tpl / "spec.template.md").read_text(encoding="utf-8").replace("<project>", args.project)
    (proj / "processed" / "spec.md").write_text(md, encoding="utf-8")
    build = (print3d_dir() / "templates" / "build.py").read_text(encoding="utf-8")
    build = re.sub(r'^NAME = "[^"]*"', f'NAME = "{args.project}"', build, count=1, flags=re.M)
    (proj / "processed" / "build.py").write_text(build, encoding="utf-8")
    print(f"created {proj}\n  input/      put photos, sketches, drawings, notes here (data only)\n"
          f"  processed/  spec.md, spec.json, build.py (template), later model/ and drawings/\n"
          f"  output/     final STL, 3MF, drawing sheet after `finalize`")
    return 0


def _load_spec(proj: Path):
    path = proj / "processed" / "spec.json"
    if not path.is_file():
        return None, [f"missing {path}"]
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except json.JSONDecodeError as exc:
        return None, [f"spec.json is not valid JSON: {exc}"]


def _build_literals(build_py: Path) -> dict:
    """UPPER_CASE literal assignments in build.py, parsed (never executed)."""
    out = {}
    tree = ast.parse(build_py.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            if name.isupper():
                try:
                    out[name] = ast.literal_eval(node.value)
                except ValueError:
                    out[name] = ...          # an expression: present, value not checkable
    return out


def check_spec(proj: Path):
    """Returns (errors, warnings)."""
    spec, errors = _load_spec(proj)
    warnings = []
    if spec is None:
        return errors, warnings
    status = spec.get("status")
    confirmed = status == "confirmed"
    if status not in STATUS:
        errors.append(f"status must be one of {sorted(STATUS)}, got {status!r}")
    if spec.get("units", "mm") != "mm":
        errors.append("units must be mm (convert every input value to mm in the spec)")
    for key in ("summary", "datum", "print", "parts"):
        if not spec.get(key):
            (errors if confirmed else warnings).append(f"'{key}' is empty")

    dims = spec.get("dimensions") or []
    ids = set()
    for i, d in enumerate(dims):
        where = f"dimensions[{i}] {d.get('id', '?')}"
        did = d.get("id")
        if not isinstance(did, str) or not re.fullmatch(r"D\d+", did):
            errors.append(f"{where}: id must look like D1, D2, ...")
        elif did in ids:
            errors.append(f"{where}: duplicate id")
        ids.add(did)
        if not isinstance(d.get("value"), (int, float)) or isinstance(d.get("value"), bool):
            errors.append(f"{where}: value must be a number in mm")
        if d.get("basis") not in BASIS:
            errors.append(f"{where}: basis must be one of {sorted(BASIS)}")
        if d.get("confidence") not in CONFIDENCE:
            errors.append(f"{where}: confidence must be one of {sorted(CONFIDENCE)}")
        if not d.get("source"):
            errors.append(f"{where}: source is empty (say where the number came from)")
        if d.get("critical") and (d.get("basis") in ("estimated", "default") or d.get("confidence") == "low"):
            msg = f"{where}: critical but {d.get('basis')}/{d.get('confidence')}: ask the user to measure it"
            (errors if confirmed else warnings).append(msg)
    if not dims:
        (errors if confirmed else warnings).append("no dimensions yet")

    for i, f in enumerate(spec.get("features") or []):
        for ref in f.get("dims", []) or []:
            if ref not in ids:
                errors.append(f"features[{i}] {f.get('id', '?')}: unknown dimension {ref}")
    for q in spec.get("open_questions") or []:
        if q.get("blocking") and not q.get("answer"):
            msg = f"open question {q.get('id', '?')} is blocking and unanswered: {q.get('question', '')}"
            (errors if confirmed else warnings).append(msg)

    build_py = proj / "processed" / "build.py"
    if build_py.is_file():
        try:
            lits = _build_literals(build_py)
        except SyntaxError as exc:
            errors.append(f"build.py does not parse: {exc}")
            lits = {}
        name = lits.get("NAME")
        if isinstance(name, str) and not NAME_RE.fullmatch(name):
            errors.append(f"build.py NAME {name!r} is not a valid part name")
        for d in dims:
            param = d.get("param")
            if not param:
                continue
            if param not in lits:
                errors.append(f"{d.get('id')}: linked param {param} is not assigned in build.py")
            elif lits[param] is not ... and isinstance(lits[param], (int, float)) and isinstance(d.get("value"), (int, float)):
                if abs(float(lits[param]) - float(d["value"])) > 1e-9:
                    errors.append(f"{d.get('id')}: spec value {d['value']} but build.py {param} = {lits[param]}")
        pr = spec.get("print") or {}
        mats = spec_materials(spec)
        if pr.get("materials") and pr.get("material") and mats[0] != pr["material"]:
            errors.append(f"print.materials[0] ({mats[0]}) must equal print.material ({pr['material']}): "
                          "the first material is the primary one that build.py and the drawings use")
        for m in mats:
            try:
                material_profile(m)
            except (ValueError, json.JSONDecodeError) as exc:
                errors.append(f"print.materials: {exc}")
        for d in dims:
            mv = d.get("material_values")
            if not mv:
                continue
            if not d.get("param"):
                errors.append(f"{d.get('id')}: material_values needs a linked param")
            for mat, val in mv.items():
                if mat.upper() not in {m.upper() for m in mats[1:]}:
                    errors.append(f"{d.get('id')}: material_values[{mat}]: not a secondary material in "
                                  f"print.materials (the primary uses `value`)")
                if not isinstance(val, (int, float)) or isinstance(val, bool):
                    errors.append(f"{d.get('id')}: material_values[{mat}] must be a number in mm")
        links = {"material": "MATERIAL", "nozzle": "NOZZLE", "layer": "LAYER",
                 "supports": "SUPPORTS_ALLOWED", "printer_bed": "PRINTER_BED"}
        for key, param in links.items():
            if key in pr and param in lits and lits[param] is not ...:
                a, b = pr[key], lits[param]
                if isinstance(a, list):
                    a = tuple(a)
                if isinstance(b, list):
                    b = tuple(b)
                if a != b:
                    errors.append(f"print.{key} = {pr[key]!r} but build.py {param} = {lits[param]!r}")
    return errors, warnings


def cmd_check(args) -> int:
    proj = project_dir(args.project)
    errors, warnings = check_spec(proj)
    for w in warnings:
        print(f"  warn   {w}")
    for e in errors:
        print(f"  ERROR  {e}")
    print("spec check: " + ("ok" if not errors else f"{len(errors)} error(s)"))
    return 1 if errors else 0


def _build(proj: Path, thin_walls: int) -> int:
    """Build the primary material (spec print.materials[0]) into processed/model/.
    It uses the same path as the release (material fits, material_values), so the
    viewer and the drawings show exactly what output/<primary>/ will hold."""
    processed = proj / "processed"
    if not (processed / "build.py").is_file():
        print("processed/build.py is missing", file=sys.stderr)
        return 2
    spec, _ = _load_spec(proj)
    mats = spec_materials(spec) if spec else []
    if not mats:
        print("spec print.material is empty", file=sys.stderr)
        return 1
    try:
        profile = material_profile(mats[0])
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 1
    fits, _src = material_fits(proj, mats[0], profile)
    tmp = processed / ".build-tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    rc = _build_material(proj, mats[0], fits, tmp, thin_walls, material_overrides(spec, mats[0]))
    if rc != 0 or not any(tmp.glob("*.stl")):
        shutil.rmtree(tmp, ignore_errors=True)
        print("build failed: processed/model/ left unchanged", file=sys.stderr)
        return rc or 1
    model = processed / "model"
    model.mkdir(exist_ok=True)
    for old in list(model.glob("*.stl")) + list(model.glob("*.json")):
        old.unlink()
    for f in tmp.iterdir():
        shutil.move(str(f), str(model / f.name))
    tmp.rmdir()
    print(f"model updated ({mats[0]}): {', '.join(p.name for p in sorted(model.glob('*.stl')))}")
    return 0


def cmd_build(args) -> int:
    proj = project_dir(args.project)
    errors, warnings = check_spec(proj)
    for w in warnings:
        print(f"  warn   {w}")
    if errors:
        for e in errors:
            print(f"  ERROR  {e}")
        if not args.force:
            print("spec check failed: fix spec.json / build.py (or --force)", file=sys.stderr)
            return 1
    return _build(proj, 0 if args.quick else 400)


def _draw(proj: Path) -> int:
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    return run([venv_python(), "-P", HERE / "draw.py", proj], env=env)


def cmd_draw(args) -> int:
    return _draw(project_dir(args.project))


def cmd_view(args) -> int:
    proj = project_dir(args.project)
    model = proj / "processed" / "model"
    if not any(model.glob("*.stl")):
        print("no model yet: run build first", file=sys.stderr)
        return 1
    cmd = [venv_python(), "-P", print3d_dir() / "scripts" / "serve.py", model, "--open"]
    if args.port:
        cmd += ["--port", str(args.port)]
    return run(cmd)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# --------------------------------------------------------------------------
# materials: one output/<MATERIAL>/ folder per material in spec print.materials
MATERIALS_DIR = SKILL_DIR / "materials"
MAT_RE = re.compile(r"^[A-Za-z0-9+-]{1,16}$")
FIT_KEYS = ("press", "snug", "sliding", "free")


def spec_materials(spec: dict) -> list[str]:
    """print.materials if given, else [print.material]. The first one is the primary
    material: build.py's MATERIAL, processed/model/ and the drawings use it."""
    pr = spec.get("print") or {}
    mats = pr.get("materials") or ([pr["material"]] if pr.get("material") else [])
    return [str(m) for m in mats]


def material_profile(name: str) -> dict:
    if not MAT_RE.fullmatch(name):
        raise ValueError(f"material name {name!r} is not valid (letters, digits, + and -)")
    path = MATERIALS_DIR / f"{name.upper()}.json"
    if not path.is_file():
        have = ", ".join(sorted(p.stem for p in MATERIALS_DIR.glob("*.json")))
        raise ValueError(f"no material profile {path.name} in {MATERIALS_DIR} (have: {have})")
    return json.loads(path.read_text(encoding="utf-8"))


def material_fits(proj: Path, name: str, profile: dict) -> tuple[dict, str]:
    """Clearances for one material: processed/fits-<MAT>.json (measured) wins over the profile."""
    own = proj / "processed" / f"fits-{name.upper()}.json"
    if own.is_file():
        data = json.loads(own.read_text(encoding="utf-8"))
        return data, f"processed/{own.name} (project, measured)"
    clear = profile.get("clearance_per_side") or {}
    data = {"material": name, "clearance_per_side": {k: clear[k] for k in FIT_KEYS if k in clear}}
    return data, f"materials/{name.upper()}.json ({profile.get('clearance_note', 'profile defaults')})"


def material_overrides(spec: dict, name: str) -> dict:
    """{PARAM: value} from dimensions[].material_values[name]. The primary material
    uses the plain `value` (the literal in build.py), so it never needs an entry."""
    out = {}
    for d in spec.get("dimensions") or []:
        mv = d.get("material_values") or {}
        for mat, val in mv.items():
            if mat.upper() == name.upper() and d.get("param"):
                out[d["param"]] = val
    return out


def _build_material(proj: Path, name: str, fits: dict, dest: Path, thin_walls: int = 400,
                    overrides: dict | None = None) -> int:
    """Build build.py with MATERIAL = name, the material's fits.json and its parameter
    overrides in a scratch folder (processed/.mat-<MAT>/), printcheck-gated, then move
    the parts into dest. build.py itself is never changed."""
    processed = proj / "processed"
    work = processed / f".mat-{name.upper()}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir()
    src = (processed / "build.py").read_text(encoding="utf-8")
    src, n = re.subn(r'^MATERIAL = "[^"]*"', f'MATERIAL = "{name}"', src, count=1, flags=re.M)
    if n != 1:
        print('build.py has no `MATERIAL = "..."` line to set per material', file=sys.stderr)
        return 2
    for param, val in (overrides or {}).items():
        if not re.fullmatch(r"[A-Z][A-Z0-9_]*", param) or not isinstance(val, (int, float)) or isinstance(val, bool):
            print(f"material_values: bad override {param} = {val!r}", file=sys.stderr)
            return 2
        src, n = re.subn(rf"^({param}\s*=\s*)[-+0-9.eE]+", rf"\g<1>{float(val)!r}", src, count=1, flags=re.M)
        if n != 1:
            print(f"material_values: build.py has no numeric literal `{param} = ...`", file=sys.stderr)
            return 2
        print(f"  {name}: {param} = {val}")
    (work / "build.py").write_text(src, encoding="utf-8")
    (work / "fits.json").write_text(json.dumps(fits, indent=2) + "\n", encoding="utf-8")
    env = dict(os.environ, PRINT3D_SKILL_DIR=str(print3d_dir()), PYTHONIOENCODING="utf-8")
    print(f"\n== {name} ==")
    rc = run([venv_python(), "-P", "build.py", "--out", "out", "--thin-walls", str(thin_walls)], cwd=work, env=env)
    if rc != 0 or not any((work / "out").glob("*.stl")):
        shutil.rmtree(work, ignore_errors=True)
        print(f"{name}: build failed, nothing released for it", file=sys.stderr)
        return rc or 1
    dest.mkdir(parents=True, exist_ok=True)
    for f in (work / "out").iterdir():
        shutil.move(str(f), str(dest / f.name))
    shutil.rmtree(work, ignore_errors=True)
    return 0


def _read_note(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip() if path.is_file() else ""


def _stem_for(project: str, part: str) -> str:
    """print.plates / print.extra_3mf name a part by its stem or by its suffix after the project name."""
    return part if part.startswith(project) else f"{project}-{part}"


def _files_row(project: str, name: str, pr: dict, metas: list) -> str:
    main = f"`{project}-{name.upper()}.3mf`"
    plates = pr.get("plates") or []
    if plates:
        main += f" ({len(plates)} plates: " + "; ".join(
            f"{i + 1}: " + ", ".join(p) for i, p in enumerate(plates)) + \
            f"; open it in Bambu Studio as a project; plate layout in `{project}-{name.upper()}-plates.svg`)"
    else:
        main += " (all parts)"
    extra = [f"`{project}-{name.upper()}-{k}.3mf` ({', '.join(v)})" for k, v in (pr.get("extra_3mf") or {}).items()]
    return "| Files | " + main + ("; " + "; ".join(extra) if extra else "") + ", or " + \
        " + ".join(f"`{m['stl']}`" for m in metas) + " |"


def write_print_sheet(proj: Path, spec: dict, name: str, profile: dict, fits_src: str, metas: list, dest: Path):
    """Generated each release, so it never goes stale. Project text comes from
    processed/print-notes.md (all materials) and processed/print-notes-<MAT>.md."""
    pr = spec.get("print") or {}
    bed = pr.get("printer_bed") or []
    project = spec.get("project", proj.name)
    lines = [f"# Print sheet: {project}, {name} (spec revision {spec.get('revision')})", "",
             f"_Generated by `pipeline.py finalize`. Edit `processed/print-notes.md` or "
             f"`processed/print-notes-{name.upper()}.md`, not this file._", "",
             "| Item | Value |", "|---|---|",
             _files_row(project, name, pr, metas)]
    for m in metas:
        sz = m.get("bbox", {}).get("size", [])
        lines.append(f"| {m['name']} | {' x '.join(f'{v:g}' for v in sz)} mm, "
                     f"{m.get('volume_mm3', 0) / 1000:.2f} cm³, at most {m.get('estimated_mass_g_solid')} g "
                     f"at 100 % infill |")
    lines += [f"| Printer | bed {' x '.join(str(b) for b in bed)}, nozzle {pr.get('nozzle')} mm, "
              f"layer {pr.get('layer')} mm |",
              f"| Orientation | {pr.get('orientation', 'as modelled')}; do not rotate |",
              f"| Supports | {'allowed' if pr.get('supports') else 'none'} |",
              f"| Quantity | {pr.get('quantity', 1)} |"]
    fits = (metas[0].get("parameters") or {}).get("FITS") or {}
    lines.append("| Fits (per side) | " + ", ".join(f"{k} {fits[k]:g}" for k in FIT_KEYS if k in fits) +
                 f"; from {fits_src} |")
    lines += ["", f"## {name} slicer settings", "", profile.get("summary", ""), "",
              "| Setting | Value | Why |", "|---|---|---|"]
    lines += [f"| {a} | {b} | {c} |" for a, b, c in profile.get("slicer", [])]
    warn = [(m["name"], f"{c.get('name')}: {c.get('message')}") for m in metas
            for c in (m.get("printcheck") or {}).get("checks", []) if c.get("status") == "warn"]
    lines += ["", "## Printcheck warnings", ""]
    lines += [f"- **{n}:** {w}" for n, w in warn] or ["- none"]
    for title, text in (("Part notes", _read_note(proj / "processed" / "print-notes.md")),
                        (f"{name} part notes", _read_note(proj / "processed" / f"print-notes-{name.upper()}.md"))):
        if text:
            lines += ["", f"## {title}", "", text]
    if profile.get("notes"):
        lines += ["", f"## {name} handling", ""] + [f"- {n}" for n in profile["notes"]]
    lines += ["", "Slicing and printing are your steps. Do not leave the printer unattended.", ""]
    (dest / "print-sheet.md").write_text("\n".join(lines), encoding="utf-8")


def _clean_output(out: Path, mats: list[str]):
    """Remove what an earlier release wrote: release files at the root (the old flat
    layout too) and the release files in every material folder. Other files stay."""
    for pat in ("*.stl", "*.3mf", "*.json", "*-drawing.svg", "*-spec.md", "print-sheet*.md"):
        for old in out.glob(pat):
            old.unlink()
    known = {p.stem.upper() for p in MATERIALS_DIR.glob("*.json")} | {m.upper() for m in mats}
    for d in out.iterdir():
        if d.is_dir() and d.name.upper() in known:
            for pat in ("*.stl", "*.3mf", "*.json", "*-plates.svg", "print-sheet.md"):
                for old in d.glob(pat):
                    old.unlink()
            if not any(d.iterdir()):
                try:
                    d.rmdir()
                except OSError:
                    pass        # held open (Windows: an Explorer window or a shell in it); it is reused


def cmd_finalize(args) -> int:
    proj = project_dir(args.project)
    spec, errs = _load_spec(proj)
    if spec is None:
        print("; ".join(errs), file=sys.stderr)
        return 1
    if spec.get("status") != "confirmed" and not args.force:
        print("spec.json status is not 'confirmed': get the user's OK on the spec first (or --force)", file=sys.stderr)
        return 1
    errors, _ = check_spec(proj)
    if errors and not args.force:
        for e in errors:
            print(f"  ERROR  {e}")
        return 1
    mats = spec_materials(spec)
    if args.material:
        mats = args.material
    if not mats:
        print("spec print.material / print.materials is empty", file=sys.stderr)
        return 1
    try:
        profiles = {m: material_profile(m) for m in mats}
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"refusing: {exc}", file=sys.stderr)
        return 1
    rc = _build(proj, 400)              # primary material: processed/model/, drawings, viewer
    if rc:
        return rc
    rc = _draw(proj)
    if rc and not args.force:
        print("drawing checks failed: the model does not match the spec (see processed/drawings/drawings.json)",
              file=sys.stderr)
        return rc

    out = proj / "output"
    out.mkdir(exist_ok=True)
    _clean_output(out, mats)
    name = args.project
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    bed = (spec.get("print") or {}).get("printer_bed") or []
    bed_arg = ["--bed", f"{bed[0]}x{bed[1]}"] if len(bed) >= 2 else []
    warnings, fits_used = {}, {}
    for mat in mats:
        dest = out / mat.upper()
        fits, fits_src = material_fits(proj, mat, profiles[mat])
        rc = _build_material(proj, mat, fits, dest, 400, material_overrides(spec, mat))
        if rc:
            return rc
        stls = sorted(dest.glob("*.stl"))
        pr = spec.get("print") or {}
        plates = pr.get("plates") or []
        if plates:
            # one Bambu/Orca plate per entry; parts not on a plate stay out of the main 3MF
            stems = {p.stem for p in stls}
            plate_stems = [[_stem_for(name, n) for n in pl] for pl in plates]
            missing = [s for pl in plate_stems for s in pl if s not in stems]
            if missing:
                print(f"print.plates names parts that were not built: {', '.join(missing)}", file=sys.stderr)
                return 1
            used = [dest / f"{s}.stl" for pl in plate_stems for s in pl]
            # the bed height and the presets let make3mf add the Bambu project config, without
            # which Bambu Studio ignores the plate list and loads everything onto one plate
            bed3 = ["--bed", "x".join(f"{float(b):g}" for b in bed[:3])] if len(bed) >= 3 else bed_arg
            preset_args = ["--nozzle", str(pr.get("nozzle") or 0.4), "--layer", str(pr.get("layer") or 0.2),
                           "--material", mat]
            if pr.get("printer"):
                preset_args += ["--printer", str(pr["printer"])]
            rc = run([venv_python(), "-P", HERE / "make3mf.py", dest / f"{name}-{mat.upper()}.3mf", *used,
                      "--title", f"{spec.get('project', name)} ({mat})", *bed3, *preset_args,
                      *[a for pl in plate_stems for a in ("--plate", ",".join(pl))]], env=env)
        else:
            rc = run([venv_python(), "-P", HERE / "make3mf.py", dest / f"{name}-{mat.upper()}.3mf", *stls,
                      "--title", f"{spec.get('project', name)} ({mat})", *bed_arg,
                      "--copies", str(int(pr.get("quantity", 1) or 1))], env=env)
        if rc:
            return rc
        for key, parts in (pr.get("extra_3mf") or {}).items():
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,31}", key):
                print(f"print.extra_3mf key {key!r}: use a-z, 0-9 and '-'", file=sys.stderr)
                return 1
            extra = [dest / f"{_stem_for(name, n)}.stl" for n in parts]
            missing = [p.name for p in extra if not p.is_file()]
            if missing:
                print(f"print.extra_3mf.{key} names parts that were not built: {', '.join(missing)}", file=sys.stderr)
                return 1
            rc = run([venv_python(), "-P", HERE / "make3mf.py", dest / f"{name}-{mat.upper()}-{key}.3mf", *extra,
                      "--title", f"{spec.get('project', name)} ({mat}, {key})", *bed_arg], env=env)
            if rc:
                return rc
        metas = [json.loads(js.read_text(encoding="utf-8")) for js in sorted(dest.glob("*.json"))]
        write_print_sheet(proj, spec, mat, profiles[mat], fits_src, metas, dest)
        fits_used[mat] = {"source": fits_src, **((metas[0].get("parameters") or {}).get("FITS") or {})}
        for meta in metas:
            warnings[f"{mat.upper()}/{meta.get('name')}"] = [
                f"{c.get('name')}: {c.get('message')}"
                for c in (meta.get("printcheck") or {}).get("checks", []) if c.get("status") == "warn"]
    sheet = proj / "processed" / "drawings" / "sheet.svg"
    if sheet.is_file():
        shutil.copy2(sheet, out / f"{name}-drawing.svg")
    spec_md = proj / "processed" / "spec.md"
    if spec_md.is_file():
        shutil.copy2(spec_md, out / f"{name}-spec.md")

    files = sorted(p for p in out.rglob("*") if p.is_file() and p.name not in (".gitkeep", "release.json"))
    release = {
        "project": name,
        "released_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "spec_revision": spec.get("revision"),
        "spec_status": spec.get("status"),
        "forced": bool(args.force),
        "materials": mats,
        "fits": fits_used,
        "files": {p.relative_to(out).as_posix(): _sha(p) for p in files},
        "printcheck_warnings": warnings,
    }
    (out / "release.json").write_text(json.dumps(release, indent=2) + "\n", encoding="utf-8")
    print(f"\nreleased to {out}:")
    for p in files:
        print(f"  {p.relative_to(out).as_posix()}")
    print("  release.json\nPart-specific print notes go in processed/print-notes.md and "
          "processed/print-notes-<MATERIAL>.md; finalize copies them into each print-sheet.md.")
    return 0


def cmd_materials(args) -> int:
    for path in sorted(MATERIALS_DIR.glob("*.json")):
        prof = json.loads(path.read_text(encoding="utf-8"))
        clear = prof.get("clearance_per_side", {})
        print(f"{path.stem:6} " + ", ".join(f"{k} {clear[k]:g}" for k in FIT_KEYS if k in clear) +
              f"  | {prof.get('summary', '')}")
    return 0


def cmd_status(args) -> int:
    proj = project_dir(args.project)
    p = proj / "processed"
    spec, _ = _load_spec(proj)
    inputs = [f.name for f in sorted((proj / "input").iterdir()) if f.name != ".gitkeep"] if (proj / "input").is_dir() else []
    rows = [
        ("input files", ", ".join(inputs) or "none"),
        ("spec", f"rev {spec.get('revision')} {spec.get('status')}, {len(spec.get('dimensions') or [])} dimensions"
         if spec else "missing"),
        ("model", ", ".join(f.name for f in sorted((p / "model").glob("*.stl"))) or "not built"),
        ("drawings", "yes" if (p / "drawings" / "sheet.svg").is_file() else "no"),
        ("output", ", ".join(f.name + ("/" if f.is_dir() else "") for f in sorted((proj / "output").iterdir())
                            if f.name != ".gitkeep") if (proj / "output").is_dir() else "empty"),
    ]
    for k, v in rows:
        print(f"{k:12} {v}")
    if not inputs:
        nxt = "add the user's photos / drawings / notes to input/"
    elif not spec or spec.get("status") != "confirmed":
        nxt = "stage 1: write spec.md + spec.json, resolve questions, get the user's OK, set status confirmed"
    elif not any((p / "model").glob("*.stl")):
        nxt = "stage 2: write build.py from the spec, then `build`"
    elif not (p / "drawings" / "sheet.svg").is_file():
        nxt = "stage 2: `draw`, then `view`"
    else:
        nxt = "stage 3: `finalize` when the user approves the drawings and the 3D view"
    print(f"{'next':12} {nxt}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="3d-design-pipeline: input -> spec -> model + drawings -> STL + 3MF")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("setup").set_defaults(fn=cmd_setup)
    for name, fn in (("new", cmd_new), ("status", cmd_status), ("check", cmd_check), ("draw", cmd_draw)):
        sp = sub.add_parser(name)
        sp.add_argument("project")
        sp.set_defaults(fn=fn)
    sp = sub.add_parser("build")
    sp.add_argument("project")
    sp.add_argument("--quick", action="store_true", help="skip the thin-wall sampling while iterating")
    sp.add_argument("--force", action="store_true", help="build even if the spec check fails")
    sp.set_defaults(fn=cmd_build)
    sp = sub.add_parser("view")
    sp.add_argument("project")
    sp.add_argument("--port", type=int, default=0)
    sp.set_defaults(fn=cmd_view)
    sp = sub.add_parser("finalize")
    sp.add_argument("project")
    sp.add_argument("--force", action="store_true", help="release despite an unconfirmed spec or failed checks")
    sp.add_argument("--material", action="append", metavar="MAT",
                    help="release only this material (repeatable); default: every one in print.materials")
    sp.set_defaults(fn=cmd_finalize)
    sub.add_parser("materials", help="list the material profiles").set_defaults(fn=cmd_materials)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
