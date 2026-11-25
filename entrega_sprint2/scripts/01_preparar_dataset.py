"""HU-02 a HU-04 — verificación de ingesta, perfilado y tratamiento de nulos.

Se ejecuta desde la raíz del repositorio. Importa los casos de uso canónicos de
ml_service/src para no duplicar reglas de negocio en la carpeta de entrega.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml_service"))

from src.application.ingestion import IngestionService  # noqa: E402
from src.application.null_treatment import NullTreatmentService  # noqa: E402
from src.application.profiling import ProfilingService  # noqa: E402
from src.infrastructure.paths import paths  # noqa: E402


def main() -> int:
    # El manifest guarda el SHA-256 del CSV crudo. Si el archivo cambia,
    # run_ingestion falla en vez de reescribirlo: así los reportes y el dataset
    # crudo no pueden quedar desalineados sin que nadie lo note.
    ingesta = IngestionService().run_ingestion(paths.raw_csv_path, paths.manifest_path)
    print(f"Ingesta: {ingesta.message}")
    print(f"Filas: {ingesta.manifest.n_rows}; columnas: {ingesta.manifest.n_columns}")
    print(f"SHA-256: {ingesta.manifest.sha256}")

    # El perfilado se escribe con fecha en el nombre; es evidencia de la fase
    # Data Understanding de CRISP-DM, no una entrada del modelo.
    reporte_perfil = paths.get_profile_report_path()
    ProfilingService().run_profiling(paths.raw_csv_path, reporte_perfil)
    print(f"Perfilado: {reporte_perfil.relative_to(ROOT)}")

    # En este dataset no hay nulos, pero las reglas quedan ejecutadas y
    # auditadas: si una entrega futura trae nulos, el mismo script los trata.
    nulos = NullTreatmentService().run(
        paths.raw_csv_path,
        paths.clean_csv_path,
        paths.null_report_path,
    )
    print(
        "Nulos: antes={0}; imputados={1}; filas eliminadas={2}".format(
            nulos.total_nulls_before,
            nulos.total_values_imputed,
            nulos.rows_dropped,
        )
    )
    pendientes = NullTreatmentService().verify_no_unexpected_nulls(paths.clean_csv_path)
    print("Nulos residuales en columnas requeridas:", pendientes or "ninguno")
    return 0 if not pendientes else 1


if __name__ == "__main__":
    raise SystemExit(main())
