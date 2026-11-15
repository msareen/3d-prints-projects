#!/usr/bin/env python3
"""install.py: install the 3d-design-pipeline skill into another repository (stdlib only).

    python install.py <target-dir> [--showcase] [--force] [--dry-run] [--no-engine]

Run it from a clone of this repo. It adds to <target-dir>:

  .claude/skills/3d-design-pipeline/    the pipeline (scripts, templates, materials, references)
  .claude/skills/3d-print-design/       the modelling engine, as a git submodule of the
                                        target (a plain clone if the target is not a git repo)
  .agents/skills/<skill>/SKILL.md       agent-neutral entry points (Codex and others)
  AGENTS.md, CLAUDE.md                  the workflow rules (appended if AGENTS.md exists)
  pyproject.toml                        the uv workspace root (only if there is none)
  .gitignore                            the pipeline's scratch folders
  --showcase: showcase/ and .github/workflows/showcase.yml (GitHub Pages site)

Existing files are never overwritten unless --force is given. Nothing is committed.
"""
from __future__ import annotations

import argparse
import configparser
import shutil
import subprocess
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent
PIPELINE = Path(".claude/skills/3d-design-pipeline")
ENGINE = Path(".claude/skills/3d-print-design")
MARKER = "<!-- 3d-design-pipeline -->"
IGNORED = shutil.ignore_patterns("__pycache__", "*.pyc", ".venv", "*.scrub.tmp")
GITIGNORE = [
    "projects/*/processed/.build-tmp/",
    "projects/*/output/.*.tmp",
    "projects/*/processed/.mat-*/",
    "projects/*/processed/model/",
    ".venv/",
    "__pycache__/",
    "_site/",
]
PYPROJECT = """# uv workspace root. The Python project itself lives in the skill:
# .claude/skills/3d-design-pipeline/pyproject.toml. From the repo root:
#   uv sync                                   create .venv with the geometry stack
#   uv run pipeline status <project>          run the design pipeline
[tool.uv.workspace]
members = [".claude/skills/3d-design-pipeline"]
"""


class Installer:
    def __init__(self, target: Path, force: bool, dry: bool):
        self.target, self.force, self.dry = target, force, dry
        self.todo: list[str] = []

    def say(self, status: str, what: str) -> None:
        print(f"  {status:9} {what}")

    def write(self, rel: Path, text: str) -> None:
        dest = self.target / rel
        if dest.exists() and not self.force:
            self.say("kept", f"{rel} (exists)")
            return
        self.say("would add" if self.dry else "added", str(rel))
        if not self.dry:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(text, encoding="utf-8", newline="\n")

    def copy_tree(self, rel: Path) -> None:
        dest = self.target / rel
        if dest.exists() and not self.force:
            self.say("kept", f"{rel}/ (exists; use --force to replace)")
            return
        self.say("would add" if self.dry else "added", f"{rel}/")
        if not self.dry:
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(SRC / rel, dest, ignore=IGNORED)

    def copy_file(self, rel: Path) -> None:
        self.write(rel, (SRC / rel).read_text(encoding="utf-8"))

    def agents(self) -> None:
        text = (SRC / "AGENTS.md").read_text(encoding="utf-8")
        dest = self.target / "AGENTS.md"
        if not dest.exists():
            self.write(Path("AGENTS.md"), text)
        elif MARKER in dest.read_text(encoding="utf-8"):
            self.say("kept", "AGENTS.md (already has the pipeline rules)")
        else:
            self.say("would edit" if self.dry else "appended", "AGENTS.md (pipeline rules added at the end)")
            if not self.dry:
                with dest.open("a", encoding="utf-8", newline="\n") as f:
                    f.write(f"\n\n{MARKER}\n{text}")
        if not (self.target / "CLAUDE.md").exists():
            self.write(Path("CLAUDE.md"), "@AGENTS.md\n")
        else:
            self.todo.append("CLAUDE.md exists: make sure it imports AGENTS.md (a line with `@AGENTS.md`).")

    def pyproject(self) -> None:
        dest = self.target / "pyproject.toml"
        if not dest.exists() or self.force:
            self.write(Path("pyproject.toml"), PYPROJECT)
        elif PIPELINE.as_posix() in dest.read_text(encoding="utf-8"):
            self.say("kept", "pyproject.toml (already lists the skill)")
        else:
            self.say("kept", "pyproject.toml (exists)")
            self.todo.append(f'add "{PIPELINE.as_posix()}" to [tool.uv.workspace] members in pyproject.toml, '
                             "or run the pipeline with python .claude/skills/3d-design-pipeline/scripts/pipeline.py.")

    def gitignore(self) -> None:
        dest = self.target / ".gitignore"
        have = dest.read_text(encoding="utf-8").splitlines() if dest.exists() else []
        missing = [g for g in GITIGNORE if g not in have]
        if not missing:
            self.say("kept", ".gitignore (up to date)")
            return
        self.say("would edit" if self.dry else "updated", f".gitignore (+{len(missing)} lines)")
        if not self.dry:
            sep = "" if not have or not dest.read_text(encoding="utf-8").strip() else "\n"
            with dest.open("a", encoding="utf-8", newline="\n") as f:
                f.write(sep + "\n".join(missing) + "\n")

    def engine(self) -> None:
        dest = self.target / ENGINE
        if (dest / "scripts" / "cad.py").is_file():
            self.say("kept", f"{ENGINE}/ (already there)")
            return
        cfg = configparser.ConfigParser()
        cfg.read(SRC / ".gitmodules", encoding="utf-8")
        section = next(s for s in cfg.sections() if cfg[s]["path"] == ENGINE.as_posix())
        url, branch = cfg[section]["url"], cfg[section].get("branch", "main")
        is_git = (self.target / ".git").exists()
        cmd = (["git", "submodule", "add", "-b", branch, url, ENGINE.as_posix()] if is_git
               else ["git", "clone", "--depth", "1", "-b", branch, url, str(dest)])
        self.say("would run" if self.dry else "running", " ".join(cmd))
        if self.dry:
            return
        res = subprocess.run(cmd, cwd=self.target if is_git else None)
        if res.returncode != 0:
            self.todo.append(f"fetching 3d-print-design failed: run `{' '.join(cmd)}` yourself.")
        elif not is_git:
            self.todo.append("the target is not a git repo, so 3d-print-design was cloned, not added as a submodule.")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("target", type=Path, help="the repository to install into (created if missing)")
    ap.add_argument("--showcase", action="store_true", help="also install the GitHub Pages showcase")
    ap.add_argument("--no-engine", action="store_true", help="skip fetching the 3d-print-design submodule")
    ap.add_argument("--force", action="store_true", help="overwrite files that already exist")
    ap.add_argument("--dry-run", action="store_true", help="show what would change and change nothing")
    args = ap.parse_args(argv)

    target = args.target.expanduser().resolve()
    if target == SRC:
        print("error: the target is this repository", file=sys.stderr)
        return 2
    if not args.dry_run:
        target.mkdir(parents=True, exist_ok=True)
    inst = Installer(target, args.force, args.dry_run)
    print(f"Installing 3d-design-pipeline into {target}" + (" (dry run)" if args.dry_run else ""))

    inst.copy_tree(PIPELINE)
    inst.copy_file(Path(".agents/skills/3d-design-pipeline/SKILL.md"))
    inst.copy_file(Path(".agents/skills/3d-print-design/SKILL.md"))
    inst.agents()
    inst.pyproject()
    inst.gitignore()
    if not args.no_engine:
        inst.engine()
    else:
        inst.todo.append(f"add the engine: git submodule add -b main <3d-print-design url> {ENGINE.as_posix()}")
    if args.showcase:
        inst.copy_tree(Path("showcase"))
        inst.copy_file(Path(".github/workflows/showcase.yml"))
        inst.todo.append("showcase: repository Settings -> Pages -> Source: GitHub Actions.")

    print("\nNext:")
    for t in inst.todo:
        print(f"  - {t}")
    print(f"  - cd {target}\n  - uv sync\n  - uv run pipeline new <project>   (or ask your agent: new project \"<name>\")")
    print("Nothing was committed: review the changes with git status.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
