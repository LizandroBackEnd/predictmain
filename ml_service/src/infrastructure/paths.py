"""Centralized workspace path resolution for PredictMain ML services."""

from pathlib import Path


def find_workspace_root(start_path: Path | None = None) -> Path:
    """Dynamically resolve the workspace root by searching for landmark files."""
    current = (start_path or Path(__file__)).resolve()
    markers = ("docker-compose.yml", "package.json", ".git")

    for candidate in [current] + list(current.parents):
        if any((candidate / marker).exists() for marker in markers):
            return candidate

    # Fallback to three levels up from this file (ml_service/src/infrastructure/paths.py)
    return Path(__file__).resolve().parents[3]


class ProjectPaths:
    """Strongly-typed project paths and directory locators."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = root or find_workspace_root()
        self.data_dir = self.root / "data"
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        self.raw_csv_path = self.raw_data_dir / "ai4i2020.csv"
        self.manifest_path = self.raw_data_dir / "manifest.json"

        self.docs_dir = self.root / "docs"
        self.analysis_docs_dir = self.docs_dir / "03-analysis"
        self.profile_report_path = self.analysis_docs_dir / "data-profile.md"

        self.ml_service_dir = self.root / "ml_service"
        self.artifacts_dir = self.ml_service_dir / "artifacts"


# Global singleton instance
paths = ProjectPaths()
