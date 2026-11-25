"""HU-08 — entrenamiento de los modelos base y serialización del seleccionado.

Se comparan regresión logística y Random Forest con la misma partición.
La selección es determinista: mayor F1, desempate por recall y luego Random Forest.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml_service"))

from src.application.baseline_training import BaselineTrainingService  # noqa: E402
from src.infrastructure.paths import paths  # noqa: E402


def main() -> int:
    # La entrada es el CSV con outliers analizados: ningún extremo se eliminó,
    # así que el modelo ve las señales de falla completas (HU-05).
    resultado = BaselineTrainingService().run(
        paths.outlier_csv_path,
        paths.model_path,
        paths.model_baseline_report_path,
    )
    print(
        f"División: {int(resultado.train_rows)}/{int(resultado.test_rows)} "
        f"(test_size={resultado.test_size}, seed={resultado.random_state})"
    )
    for fila in resultado.metrics:
        print(
            f"{fila.name}: accuracy={fila.accuracy:.4f} precision={fila.precision:.4f} "
            f"recall={fila.recall:.4f} f1={fila.f1:.4f} roc_auc={fila.roc_auc:.4f}"
        )
    print(f"Seleccionado: {resultado.selected_model}")
    print(f"Artefacto: {resultado.model_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
