#!/usr/bin/env python3
"""showcase/build.py: build the static project showcase (stdlib only).

Reads every released project under projects/ (one with output/release.json) and
writes a self-contained static site:

    <out>/index.html, showcase.css, showcase.js, viewer.js   copied from showcase/
    <out>/projects.json                                     the index the page reads
    <out>/projects/<project>/...                            the published files

Published per project: the input photos, sketches and brief (input/), the
photos of the printed part (output/printed-pic/), the preview renders (processed/drawings/preview*)
and the release (the rest of output/: STL, 3MF, print sheets, drawing, spec, release.json).
build.py, spec.json and the other working files stay in the repository.

By default only files tracked by git are published, so a local build shows
exactly what GitHub Pages will show. The build fails if any published photo still
carries GPS coordinates (run `uv run pipeline scrub <project>` first).

    python showcase/build.py                       -> _site/
    python showcase/build.py --out DIR --untracked  include files not yet committed
    python -m http.server -d _site 8000             preview at http://127.0.0.1:8000/
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PROJECTS = REPO / "projects"
sys.path.insert(0, str(REPO / ".claude" / "skills" / "3d-design-pipeline" / "scripts"))
import scrub  # noqa: E402  (stdlib-only GPS check shared with the pipeline)

STATIC = ("index.html", "showcase.css", "showcase.js", "viewer.js")
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".svg"}         # what a browser shows and scrub can check
INPUT_EXT = IMAGE_EXT | {".pdf"}
SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
SAFE_MAT = re.compile(r"^[A-Za-z0-9_-]{1,16}$")
# a published relative path: no control characters, no '..', no backslashes, no leading dot
SAFE_REL = re.compile(r"^(?!.*(?:^|/)\.)[^\x00-\x1f\\<>\"|?*]{1,200}$")


def tracked_files() -> set[str] | None:
    """Repo-relative POSIX paths tracked by git under projects/, or None without git."""
    try:
        out = subprocess.run(["git", "-C", str(REPO), "ls-files", "-z", "projects"],
                             capture_output=True, check=True).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {p for p in out.decode("utf-8").split("\0") if p}


def repo_url() -> str:
    if os.environ.get("GITHUB_REPOSITORY"):
        return f"{os.environ.get('GITHUB_SERVER_URL', 'https://github.com')}/{os.environ['GITHUB_REPOSITORY']}"
    try:
        url = subprocess.run(["git", "-C", str(REPO), "remote", "get-url", "origin"],
                             capture_output=True, text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""
    m = re.match(r"^(?:https://github\.com/|git@github\.com:)([\w.-]+/[\w.-]+?)(?:\.git)?$", url)
    return f"https://github.com/{m.group(1)}" if m else ""


def title_of(slug: str) -> str:
    return slug.replace("-", " ").capitalize()


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


class Site:
    def __init__(self, out: Path, tracked: set[str] | None):
        self.out = out
        self.tracked = tracked
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def published(self, path: Path) -> bool:
        if not path.is_file() or path.name == ".gitkeep":
            return False
        rel = path.relative_to(REPO).as_posix()
        if self.tracked is not None and rel not in self.tracked:
            return False
        if not SAFE_REL.match(path.relative_to(PROJECTS).as_posix()):
            self.warnings.append(f"skipped {rel}: unusual characters in the path")
            return False
        return True

    def files(self, folder: Path, exts: set[str] | None = None) -> list[Path]:
        if not folder.is_dir():
            return []
        return [p for p in sorted(folder.rglob("*"))
                if self.published(p) and (exts is None or p.suffix.lower() in exts)]

    def copy(self, path: Path) -> str:
        """Copy one project file into the site; returns its site-relative URL path."""
        rel = path.relative_to(REPO).as_posix()
        if path.suffix.lower() in scrub.JPEG_EXT | scrub.PNG_EXT and scrub.find_gps(path) == "gps":
            self.errors.append(f"{rel} carries GPS coordinates: run `uv run pipeline scrub "
                               f"{path.relative_to(PROJECTS).parts[0]}`")
        dest = self.out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, dest)
        return rel


def cover_rank(e: dict):
    """Pick the main render as the card picture: preview.png, then an iso view, PNG before SVG."""
    stem, ext = e["name"].rsplit(".", 1)
    return (0 if stem == "preview" else 1 if "iso" in stem else 2, ext != "png", e["name"])


def file_entry(site: Site, path: Path, kind: str) -> dict:
    return {"path": site.copy(path), "name": path.name, "kind": kind, "bytes": path.stat().st_size}


def build_project(site: Site, proj: Path) -> dict | None:
    slug = proj.name
    spec = read_json(proj / "processed" / "spec.json")
    release = read_json(proj / "output" / "release.json")
    if not SAFE_SLUG.match(slug) or not spec or not release:
        return None
    if not site.published(proj / "output" / "release.json"):
        return None
    pr = spec.get("print") or {}
    materials = [m for m in (release.get("materials") or []) if isinstance(m, str) and SAFE_MAT.match(m)]
    notes = {str(i.get("file", "")).replace("\\", "/"): str(i.get("notes", ""))
             for i in spec.get("inputs") or [] if isinstance(i, dict)}

    brief_path = proj / "input" / "brief.md"
    brief = brief_path.read_text(encoding="utf-8") if site.published(brief_path) else ""
    inputs = []
    for f in site.files(proj / "input", INPUT_EXT):
        e = file_entry(site, f, "pdf" if f.suffix.lower() == ".pdf" else "image")
        e["notes"] = notes.get(f.relative_to(proj).as_posix(), "")
        inputs.append(e)
    printed = [file_entry(site, f, "image") for f in site.files(proj / "output" / "printed-pic", IMAGE_EXT)]
    renders = [file_entry(site, f, "image") for f in site.files(proj / "processed" / "drawings", IMAGE_EXT)
               if f.name.startswith("preview")]
    for folder in ("input", "output/printed-pic"):
        for f in site.files(proj / folder):
            if f.suffix.lower() in scrub.OTHER_IMAGE_EXT:
                site.warnings.append(f"skipped {f.relative_to(REPO).as_posix()}: convert it to JPEG to publish it")

    out_dir = proj / "output"
    shared, per_mat = [], {}
    for f in site.files(out_dir):
        rel = f.relative_to(out_dir)
        if len(rel.parts) == 1:
            if f.name == "release.json":
                shared.append(file_entry(site, f, "release"))
            elif f.name.endswith("-drawing.svg"):
                shared.append(file_entry(site, f, "drawing"))
            elif f.name.endswith("-spec.md"):
                shared.append(file_entry(site, f, "spec"))
            continue
        mat = rel.parts[0]
        if mat not in materials or len(rel.parts) != 2:
            continue
        ext = f.suffix.lower()
        kind = {".3mf": "3mf", ".stl": "stl", ".md": "sheet", ".svg": "plates"}.get(ext)
        if not kind:
            continue
        e = file_entry(site, f, kind)
        if kind == "stl":
            meta = read_json(f.with_suffix(".json")) or {}
            e["part"] = str(meta.get("name") or f.stem)
            e["mass_g"] = meta.get("estimated_mass_g_solid")
            e["size_mm"] = (meta.get("bbox") or {}).get("size")
        per_mat.setdefault(mat, []).append(e)
    order = {"3mf": 0, "stl": 1, "sheet": 2, "plates": 3}
    downloads = [{"material": m, "files": sorted(per_mat[m], key=lambda e: (order[e["kind"]], e["name"]))}
                 for m in materials if m in per_mat]
    drawing = next((e for e in shared if e["kind"] == "drawing"), None)
    shared.sort(key=lambda e: ("drawing", "spec", "release").index(e["kind"]))
    cover = printed[0] if printed else (min(renders, key=cover_rank) if renders else drawing)

    return {
        "slug": slug,
        "title": title_of(slug),
        "summary": str(spec.get("summary") or ""),
        "revision": release.get("spec_revision", spec.get("revision")),
        "released_utc": release.get("released_utc"),
        "materials": materials,
        "envelope": spec.get("envelope"),
        "printer_bed": pr.get("printer_bed"),
        "layer": pr.get("layer"),
        "nozzle": pr.get("nozzle"),
        "orientation": pr.get("orientation"),
        "parts": [{"name": str(p.get("name", "")), "description": str(p.get("description", ""))}
                  for p in spec.get("parts") or [] if isinstance(p, dict)],
        "brief": brief,
        "inputs": inputs,
        "printed": printed,
        "renders": renders,
        "shared": shared,
        "downloads": downloads,
        "cover": cover["path"] if cover else None,
        "source": f"projects/{slug}",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(REPO / "_site"), help="output folder (default: _site/)")
    ap.add_argument("--untracked", action="store_true", help="also publish files git does not track yet")
    args = ap.parse_args(argv)

    out = Path(args.out).resolve()
    if out == REPO or REPO.is_relative_to(out) or out.is_relative_to(PROJECTS) or out.is_relative_to(HERE):
        print(f"refusing to write the site to {out}", file=sys.stderr)
        return 2
    tracked = None if args.untracked else tracked_files()
    if tracked is None and not args.untracked:
        print("git is not available: publishing every file under projects/", file=sys.stderr)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    site = Site(out, tracked)

    projects = [p for p in (build_project(site, d) for d in sorted(PROJECTS.iterdir()) if d.is_dir()) if p]
    projects.sort(key=lambda p: p.get("released_utc") or "", reverse=True)
    for name in STATIC:
        shutil.copyfile(HERE / name, out / name)
    (out / ".nojekyll").touch()
    index = {
        "generated_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "repo": repo_url(),
        "projects": projects,
    }
    (out / "projects.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    for w in site.warnings:
        print(f"  warn  {w}", file=sys.stderr)
    if site.errors:
        for e in site.errors:
            print(f"  ERROR {e}", file=sys.stderr)
        shutil.rmtree(out, ignore_errors=True)
        print("showcase not built: fix the errors above", file=sys.stderr)
        return 1
    size = sum(f.stat().st_size for f in out.rglob("*") if f.is_file())
    print(f"showcase: {len(projects)} project(s), {size / 1e6:.1f} MB -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
