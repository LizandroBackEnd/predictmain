"""Infrastructure adapter for ML pipeline persistence using joblib."""

from pathlib import Path

import joblib
from sklearn.pipeline import Pipeline


def save_pipeline(pipeline: Pipeline, path: Path) -> None:
    """Serialize a fitted sklearn Pipeline to disk.

    Raises:
        ValueError: if the pipeline object is None.
    """
    if pipeline is None:
        raise ValueError("Cannot save a None pipeline.")
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, path)


def load_pipeline(path: Path) -> Pipeline:
    """Deserialize a previously saved sklearn Pipeline from disk.

    Raises:
        FileNotFoundError: if the artifact does not exist at the given path.
    """
    if not path.exists():
        raise FileNotFoundError(f"Pipeline artifact not found: {path}")
    return joblib.load(path)

