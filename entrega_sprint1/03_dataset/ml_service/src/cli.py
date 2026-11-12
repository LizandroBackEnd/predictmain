"""Unified Command Line Interface for PredictMain Data & ML Pipelines.

Backward-compatible forwarder delegating to src.interfaces.cli.entrypoint.
"""

import sys

from src.interfaces.cli.entrypoint import main

if __name__ == "__main__":
    sys.exit(main())
