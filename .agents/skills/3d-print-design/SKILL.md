---
name: 3d-print-design
description: Design or adapt an FDM-printable 3D part, including printability checks, tolerances, STL output, and local preview. Use for standalone work outside the repository pipeline.
---

# 3D-print design compatibility entry point

This is the agent-neutral discovery entry point. The authoritative upstream
skill is the repository submodule at
`../../../.claude/skills/3d-print-design/`; it remains there for Claude Code
compatibility.

Before acting on a standalone 3D-print-design request, read the complete
authoritative skill:

`../../../.claude/skills/3d-print-design/SKILL.md`

The relative paths above are relative to this entry point's directory.
Resolve the authoritative skill's references and `$SKILL` from its canonical
`.claude/skills/3d-print-design/` directory, not from this wrapper.

For design work in this repository, use `3d-design-pipeline` first, as required
by AGENTS.md; it selects the relevant upstream modelling steps. Do not edit,
copy, or fork the submodule from this compatibility entry point.
