"""CLI entrypoint and argument parser for PredictMain pipelines."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.infrastructure.paths import paths
from src.interfaces.cli.commands import (
    run_ingestion_cmd,
    run_null_treatment_cmd,
    run_outlier_analysis_cmd,
    run_profiling_cmd,
    run_transform_cmd,
)


def build_parser() -> argparse.ArgumentParser:
    """Configure command-line arguments and subcommands."""
    parser = argparse.ArgumentParser(
        prog="predictmain-pipeline",
        description="CLI para pipelines de datos y ML de PredictMain (Clean Architecture)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")

    # Ingestion command
    ingest = subparsers.add_parser("ingest", help="Ejecutar ingesta y generar manifest.json (HU-01)")
    ingest.add_argument("--csv", type=Path, default=paths.raw_csv_path, help="Ruta al archivo CSV crudo")
    ingest.add_argument("--manifest", type=Path, default=paths.manifest_path, help="Ruta al manifest JSON de salida")

    # Profiling command
    profile = subparsers.add_parser("profile", help="Ejecutar perfilado estadístico y generar reporte (HU-02)")
    profile.add_argument("--csv", type=Path, default=paths.raw_csv_path, help="Ruta al archivo CSV crudo a perfilar")
    profile.add_argument("--report", type=Path, default=paths.get_profile_report_path(), help="Ruta al reporte Markdown de salida")

    # Null treatment command
    treat = subparsers.add_parser("treat", help="Tratar valores nulos y generar null_report.md (HU-04)")
    treat.add_argument("--csv", type=Path, default=paths.raw_csv_path)
    treat.add_argument("--output", type=Path, default=paths.clean_csv_path)
    treat.add_argument("--report", type=Path, default=paths.null_report_path)

    # Outlier analysis command
    outliers = subparsers.add_parser("outliers", help="Analizar outliers y generar outlier_report.md (HU-05)")
    outliers.add_argument("--csv", type=Path, default=paths.clean_csv_path)
    outliers.add_argument("--output", type=Path, default=paths.outlier_csv_path)
    outliers.add_argument("--report", type=Path, default=paths.outlier_report_path)

    # Transformation pipeline command
    transform = subparsers.add_parser("transform", help="Ajustar pipeline y generar features (HU-06)")
    transform.add_argument("--csv", type=Path, default=paths.outlier_csv_path)
    transform.add_argument("--output", type=Path, default=paths.transformed_csv_path)
    transform.add_argument("--pipeline", type=Path, default=paths.pipeline_path)

    # All command
    all_cmd = subparsers.add_parser("all", help="Ejecutar ingesta, perfilado y tratamiento de extremo a extremo")
    all_cmd.add_argument("--csv", type=Path, default=paths.raw_csv_path, help="Ruta al archivo CSV crudo")

    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse CLI arguments and dispatch commands."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "ingest":
        return run_ingestion_cmd(args.csv, args.manifest)
    if args.command == "profile":
        return run_profiling_cmd(args.csv, args.report)
    if args.command == "treat":
        return run_null_treatment_cmd(args.csv, args.output, args.report)
    if args.command == "outliers":
        return run_outlier_analysis_cmd(args.csv, args.output, args.report)
    if args.command == "transform":
        return run_transform_cmd(args.csv, args.output, args.pipeline)
    if args.command == "all":
        if (code := run_ingestion_cmd(args.csv, paths.manifest_path)) != 0:
            return code
        if (code := run_profiling_cmd(args.csv, paths.get_profile_report_path())) != 0:
            return code
        if (code := run_null_treatment_cmd(args.csv, paths.clean_csv_path, paths.null_report_path)) != 0:
            return code
        if (code := run_outlier_analysis_cmd(paths.clean_csv_path, paths.outlier_csv_path, paths.outlier_report_path)) != 0:
            return code
        return run_transform_cmd(paths.outlier_csv_path, paths.transformed_csv_path, paths.pipeline_path)

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

