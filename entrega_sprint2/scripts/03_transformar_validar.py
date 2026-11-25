"""HU-06 y HU-07 — transformación sin fuga y validación de la matriz.

El escalador y el codificador se ajustan solo con el 80% de entrenamiento.
El 20% restante se transforma sin re-ajustar; después se validan las 8 columnas.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml_service"))

from src.application.dataset_split import split_dataset  # noqa: E402
from src.application.matrix_validation import validate_feature_matrix  # noqa: E402
from src.application.transformation import TransformationService  # noqa: E402
from src.domain.models import MatrixValidationResult  # noqa: E402
from src.infrastructure.paths import paths  # noqa: E402
from src.infrastructure.reporting import build_matrix_validation_report  # noqa: E402


def main() -> int:
    df = pd.read_csv(paths.outlier_csv_path)
    particion = split_dataset(df, target_column="Machine failure")

    # fit_transform sobre entrenamiento; transform sobre prueba. Este orden es
    # la barrera anti-leakage: la media y la desviación nunca ven el test.
    X_train, y_train = TransformationService.split_features_target(particion.train)
    X_test, _ = TransformationService.split_features_target(particion.test)
    transformador = TransformationService()
    X_train_t = transformador.fit_transform(X_train)
    X_test_t = transformador.transform(X_test)
    transformador.save(paths.pipeline_path)
    print(f"Fit: {len(X_train_t)} filas; transform: {len(X_test_t)} filas")

    # El CSV transformado conserva las 10 000 filas para trazabilidad. La
    # partición 75/25 del entrenamiento se reconstruye después con la semilla.
    aplicador = TransformationService()
    aplicador.load(paths.pipeline_path)
    completa = aplicador.transform(TransformationService.split_features_target(df)[0])
    completa["Machine failure"] = df["Machine failure"].to_numpy()
    completa.to_csv(paths.transformed_csv_path, index=False)

    matriz = validate_feature_matrix(
        completa.drop(columns=["Machine failure"]),
        y=completa["Machine failure"],
        source_file=paths.transformed_csv_path.name,
    )
    validacion: MatrixValidationResult = matriz
    paths.matrix_validation_report_path.parent.mkdir(parents=True, exist_ok=True)
    paths.matrix_validation_report_path.write_text(
        build_matrix_validation_report(validacion), encoding="utf-8"
    )
    completa.drop(columns=["Machine failure"]).to_csv(
        paths.feature_matrix_csv_path, index=False
    )
    print(f"Matriz: {len(matriz.checks)} controles; aprobada={matriz.passed}")
    print(f"Columnas: {', '.join(completa.columns[:-1])}")
    return 0 if matriz.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
