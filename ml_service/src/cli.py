"""Unified Command Line Interface for PredictMain Data & ML Pipelines."""

import argparse
import sys
from pathlib import Path

from src.infrastructure.paths import paths
from src.ingestion.service import IngestionService
from src.profiling.service import ProfilingService
from src.null_treatment.service import NullTreatmentService
from src.outlier_analysis.service import OutlierAnalysisService


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


def run_null_treatment_cmd(csv_path: Path, output_csv: Path, report_path: Path) -> int:
    """Execute null treatment pipeline and generate null report (HU-04)."""
    print("=" * 60)
    print("🧹 PredictMain — HU-04: Tratamiento de Valores Nulos")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Salida limpia:  {output_csv}")
    print(f"Reporte:        {report_path}")
    print()

    service = NullTreatmentService()
    try:
        result = service.run(csv_path=csv_path, output_csv_path=output_csv, report_path=report_path)
        print(f"✅ Pipeline completado.")
        print(f"• Filas antes:           {result.rows_before:,}")
        print(f"• Filas con nulos:       {result.rows_with_nulls_before:,}")
        print(f"• Total nulos:           {result.total_nulls_before:,}")
        print(f"• Filas eliminadas:      {result.rows_dropped:,}")
        print(f"• Valores imputados:     {result.total_values_imputed:,}")
        print(f"• Filas en salida:       {result.rows_after:,}")
        print()

        remaining = service.verify_no_unexpected_nulls(output_csv)
        if remaining:
            print(f"⚠️  Nulos inesperados en: {remaining}", file=sys.stderr)
            return 1
        print("✅ Verificación post-tratamiento: sin nulos inesperados.")
        print()
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error durante el tratamiento: {exc}", file=sys.stderr)
        return 1


def run_outlier_analysis_cmd(csv_path: Path, output_csv: Path, report_path: Path) -> int:
    """Execute outlier analysis and generate outlier_report.md (HU-05)."""
    print("=" * 60)
    print("📊 PredictMain — HU-05: Análisis de Valores Atípicos")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Salida:         {output_csv}")
    print(f"Reporte:        {report_path}")
    print()

    service = OutlierAnalysisService()
    try:
        result = service.run(csv_path=csv_path, output_csv_path=output_csv, report_path=report_path)
        print("✅ Análisis completado.")
        print(f"• Registros entrada:     {result.rows_input:,}")
        print(f"• Outliers detectados:   {result.total_detected:,}")
        print(f"• Valores modificados:   {result.total_modified:,}")
        print(f"• Filas excluidas:       {result.total_excluded:,}")
        print(f"• Registros salida:      {result.rows_output:,}")
        print()
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error durante el análisis: {exc}", file=sys.stderr)
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

    # Null treatment command
    treat_parser = subparsers.add_parser("treat", help="Tratar valores nulos y generar null_report.md (HU-04)")
    treat_parser.add_argument("--csv", type=Path, default=paths.raw_csv_path)
    treat_parser.add_argument("--output", type=Path, default=paths.clean_csv_path)
    treat_parser.add_argument("--report", type=Path, default=paths.null_report_path)

    # Outlier analysis command
    outlier_parser = subparsers.add_parser("outliers", help="Analizar outliers y generar outlier_report.md (HU-05)")
    outlier_parser.add_argument("--csv",    type=Path, default=paths.clean_csv_path)
    outlier_parser.add_argument("--output", type=Path, default=paths.outlier_csv_path)
    outlier_parser.add_argument("--report", type=Path, default=paths.outlier_report_path)

    # All command
    all_parser = subparsers.add_parser("all", help="Ejecutar ingesta, perfilado y tratamiento de extremo a extremo")
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
    elif args.command == "treat":
        return run_null_treatment_cmd(args.csv, args.output, args.report)
    elif args.command == "outliers":
        return run_outlier_analysis_cmd(args.csv, args.output, args.report)
    elif args.command == "all":
        ingest_exit = run_ingestion_cmd(args.csv, paths.manifest_path)
        if ingest_exit != 0:
            return ingest_exit
        profile_exit = run_profiling_cmd(args.csv, paths.get_profile_report_path())
        if profile_exit != 0:
            return profile_exit
        treat_exit = run_null_treatment_cmd(args.csv, paths.clean_csv_path, paths.null_report_path)
        if treat_exit != 0:
            return treat_exit
        return run_outlier_analysis_cmd(paths.clean_csv_path, paths.outlier_csv_path, paths.outlier_report_path)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
