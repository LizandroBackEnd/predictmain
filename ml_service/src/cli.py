"""Unified Command Line Interface for PredictMain Data & ML Pipelines."""

import argparse
import sys
from pathlib import Path

from src.infrastructure.paths import paths
from src.ingestion.service import IngestionService
from src.profiling.service import ProfilingService


def run_ingestion_cmd(csv_path: Path, manifest_path: Path) -> int:
    """Execute raw dataset ingestion and manifest generation."""
    print("=" * 60)
    print("🚀 PredictMain — HU-01: Ingesta de Datos Crudos")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Manifest JSON:  {manifest_path}")
    print()

    service = IngestionService()
    try:
        result = service.run_ingestion(csv_path=csv_path, manifest_path=manifest_path)
        print(f"✅ {result.message}")
        print(f"• Filas de datos:    {result.manifest.n_rows:,}")
        print(f"• Columnas:          {result.manifest.n_columns}")
        print(f"• Tamaño archivo:    {result.manifest.size_bytes:,} bytes")
        print(f"• SHA-256:           {result.manifest.sha256}")
        print(f"• Inalterado:        {not result.manifest.transformed}")
        print()
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error durante la ingesta: {exc}", file=sys.stderr)
        return 1


def run_profiling_cmd(csv_path: Path, report_path: Path) -> int:
    """Execute dataset profiling and documentation generation."""
    print("=" * 60)
    print("📊 PredictMain — HU-02: Perfilado de Telemetría Histórica")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Reporte MD:     {report_path}")
    print()

    service = ProfilingService()
    try:
        summary = service.run_profiling(csv_path=csv_path, output_report_path=report_path)
        print("✅ Perfilado estadístico completado correctamente.")
        print(f"• Filas analizadas:  {summary.total_rows:,}")
        print(f"• Columnas:          {summary.total_columns}")
        if summary.target_distribution:
            dist_str = ", ".join(f"Clase {k}: {v:,}" for k, v in summary.target_distribution.items())
            print(f"• Distribución falla: {dist_str}")
        print(f"• Documento escrito: {report_path}")
        print()
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error durante el perfilado: {exc}", file=sys.stderr)
        return 1


def main() -> int:
    """Parse CLI arguments and dispatch commands."""
    parser = argparse.ArgumentParser(
        prog="predictmain-pipeline",
        description="CLI para pipelines de datos y ML de PredictMain (Clean Architecture)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Ingestion command
    ingest_parser = subparsers.add_parser("ingest", help="Ejecutar ingesta y generar manifest.json (HU-01)")
    ingest_parser.add_argument(
        "--csv",
        type=Path,
        default=paths.raw_csv_path,
        help="Ruta al archivo CSV crudo (por defecto data/raw/ai4i2020.csv)",
    )
    ingest_parser.add_argument(
        "--manifest",
        type=Path,
        default=paths.manifest_path,
        help="Ruta al manifest JSON de salida",
    )

    # Profiling command
    profile_parser = subparsers.add_parser("profile", help="Ejecutar perfilado estadístico y generar reporte (HU-02)")
    profile_parser.add_argument(
        "--csv",
        type=Path,
        default=paths.raw_csv_path,
        help="Ruta al archivo CSV crudo a perfilar",
    )
    profile_parser.add_argument(
        "--report",
        type=Path,
        default=paths.get_profile_report_path(),
        help="Ruta al reporte Markdown de salida",
    )

    # All command
    all_parser = subparsers.add_parser("all", help="Ejecutar ingesta y perfilado de extremo a extremo")
    all_parser.add_argument(
        "--csv",
        type=Path,
        default=paths.raw_csv_path,
        help="Ruta al archivo CSV crudo",
    )

    args = parser.parse_args()

    if args.command == "ingest":
        return run_ingestion_cmd(args.csv, args.manifest)
    elif args.command == "profile":
        return run_profiling_cmd(args.csv, args.report)
    elif args.command == "all":
        ingest_exit = run_ingestion_cmd(args.csv, paths.manifest_path)
        if ingest_exit != 0:
            return ingest_exit
        return run_profiling_cmd(args.csv, paths.get_profile_report_path())
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
