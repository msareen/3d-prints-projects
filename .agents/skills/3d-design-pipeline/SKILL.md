---
name: 3d-design-pipeline
description: Use the repository's checked 3D-print design pipeline for a part described by photos, sketches, drawings, measurements, or text. Covers specification, parametric modelling, checked drawings, and STL/3MF release.
---

# 3D design pipeline compatibility entry point

This is the agent-neutral discovery entry point. The authoritative skill and
all of its scripts, templates, material profiles, and references are kept at
`../../../.claude/skills/3d-design-pipeline/` so Claude Code can continue to
discover the same implementation.

Before acting on a 3D-design request, read the complete authoritative skill:

`../../../.claude/skills/3d-design-pipeline/SKILL.md`

The relative paths above are relative to this entry point's directory.
Resolve references inside the authoritative skill relative to its own directory;
`$PIPE` and `$P3D` refer to the canonical `.claude/skills/` folders.
Run commands from the repository root;
do not copy, edit, or fork the implementation merely because this compatibility
entry point is in `.agents/`.
