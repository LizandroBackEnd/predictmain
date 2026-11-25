"""HU-05 — análisis de valores atípicos con IQR 1.5 y percentiles P1/P99.

La decisión por sensor está en src/domain/outlier_rules.py. Aquí solo se
orquesta la ejecución y se imprime el resultado; las reglas viven en dominio.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml_service"))

from src.application.outlier_analysis import OutlierAnalysisService  # noqa: E402
from src.infrastructure.paths import paths  # noqa: E402


def main() -> int:
    # KEEP es la regla para los cinco sensores: los extremos de RPM y torque
    # son precursores de falla y los de temperatura/desgaste son válidos según
    # los rangos físicos UCI. Eliminarlos destruiría señal predictiva.
    resultado = OutlierAnalysisService().run(
        paths.clean_csv_path,
        paths.outlier_csv_path,
        paths.outlier_report_path,
    )
    print(f"Filas de entrada/salida: {resultado.rows_input}/{resultado.rows_output}")
    print(f"Outliers detectados: {resultado.total_detected}")
    print(f"Valores modificados: {resultado.total_modified}")
    print(f"Filas excluidas: {resultado.total_excluded}")
    for stat in resultado.column_stats:
        print(
            f"  {stat.column}: IQR={stat.iqr_outliers_count}, "
            f"P1/P99={stat.percentile_outliers_count}, "
            f"decisión={stat.decision}, tipo={stat.outlier_type}"
        )
    print(f"Reporte: {resultado.source_file} -> {paths.outlier_report_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
