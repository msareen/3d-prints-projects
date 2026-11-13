"""Entry point for `uv run pipeline ...`: runs scripts/pipeline.py from this skill folder."""
from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
    import pipeline  # noqa: E402  (scripts/pipeline.py)

    return pipeline.main()


if __name__ == "__main__":
    sys.exit(main())
