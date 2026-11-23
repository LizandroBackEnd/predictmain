"""Local FastAPI dev server for PredictMain ML inference.

Usage (from ml_service/):

    .venv/bin/python dev.py

Or from the repo root:

    bun run dev:ml
"""

from __future__ import annotations

import os
import sys
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parent
    root_str = str(root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    os.environ["PYTHONPATH"] = root_str

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[root_str],
    )


if __name__ == "__main__":
    main()
