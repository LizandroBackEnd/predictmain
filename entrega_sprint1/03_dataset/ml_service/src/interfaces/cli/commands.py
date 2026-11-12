"""Command handlers for PredictMain data & ML CLI."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.application.ingestion import IngestionService
from src.application.null_treatment import NullTreatmentService
from src.application.outlier_analysis import OutlierAnalysisService
from src.application.profiling import ProfilingService
from src.application.transformation import TransformationService


def run_ingestion_cmd(csv_path: Path, manifest_path: Path) -> int:
    """Execute raw dataset ingestion and manifest generation."""
    print("=" * 60)
    print("🚀 PredictMain — HU-01: Ingesta de Datos Crudos")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Manifest JSON:  {manifest_path}\n")

    service = IngestionService()
    try:
        result = service.run_ingestion(csv_path=csv_path, manifest_path=manifest_path)
        print(f"✅ {result.message}")
        print(f"• Filas de datos:    {result.manifest.n_rows:,}")
        print(f"• Columnas:          {result.manifest.n_columns}")
        print(f"• Tamaño archivo:    {result.manifest.size_bytes:,} bytes")
        print(f"• SHA-256:           {result.manifest.sha256}")
        print(f"• Inalterado:        {not result.manifest.transformed}\n")
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
    print(f"Reporte MD:     {report_path}\n")

    service = ProfilingService()
    try:
        summary = service.run_profiling(csv_path=csv_path, output_report_path=report_path)
        print("✅ Perfilado estadístico completado correctamente.")
        print(f"• Filas analizadas:  {summary.total_rows:,}")
        print(f"• Columnas:          {summary.total_columns}")
        if summary.target_distribution:
            dist_str = ", ".join(f"Clase {k}: {v:,}" for k, v in summary.target_distribution.items())
            print(f"• Distribución falla: {dist_str}")
        print(f"• Documento escrito: {report_path}\n")
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
    print(f"Reporte:        {report_path}\n")

    service = NullTreatmentService()
    try:
        result = service.run(csv_path=csv_path, output_csv_path=output_csv, report_path=report_path)
        print("✅ Pipeline completado.")
        print(f"• Filas antes:           {result.rows_before:,}")
        print(f"• Filas con nulos:       {result.rows_with_nulls_before:,}")
        print(f"• Total nulos:           {result.total_nulls_before:,}")
        print(f"• Filas eliminadas:      {result.rows_dropped:,}")
        print(f"• Valores imputados:     {result.total_values_imputed:,}")
        print(f"• Filas en salida:       {result.rows_after:,}\n")

        remaining = service.verify_no_unexpected_nulls(output_csv)
        if remaining:
            print(f"⚠️  Nulos inesperados en: {remaining}", file=sys.stderr)
            return 1
        print("✅ Verificación post-tratamiento: sin nulos inesperados.\n")
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
    print(f"Reporte:        {report_path}\n")

    service = OutlierAnalysisService()
    try:
        result = service.run(csv_path=csv_path, output_csv_path=output_csv, report_path=report_path)
        print("✅ Análisis completado.")
        print(f"• Registros entrada:     {result.rows_input:,}")
        print(f"• Outliers detectados:   {result.total_detected:,}")
        print(f"• Valores modificados:   {result.total_modified:,}")
        print(f"• Filas excluidas:       {result.total_excluded:,}")
        print(f"• Registros salida:      {result.rows_output:,}\n")
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error durante el análisis: {exc}", file=sys.stderr)
        return 1


def run_transform_cmd(csv_path: Path, output_csv: Path, pipeline_path: Path) -> int:
    """Fit transformation pipeline on training data and serialize it (HU-06)."""
    print("=" * 60)
    print("⚙️  PredictMain — HU-06: Pipeline de Transformación")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Salida CSV:     {output_csv}")
    print(f"Pipeline:       {pipeline_path}\n")

    service = TransformationService()
    try:
        df = pd.read_csv(csv_path)
        X, y = service.split_features_target(df)
        X_transformed = service.fit_transform(X)

        missing = service.verify_output(X_transformed)
        if missing:
            print(f"❌ Columnas faltantes en la salida: {missing}", file=sys.stderr)
            return 1

        service.save(pipeline_path)

        out_df = X_transformed.copy()
        out_df[y.name] = y.values
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_csv, index=False)

        print("✅ Pipeline ajustado y guardado.")
        print(f"• Filas transformadas:   {len(X_transformed):,}")
        print(f"• Columnas de features:  {len(X_transformed.columns)}")
        print(f"• Columnas: {list(X_transformed.columns)}")
        print(f"• Pipeline guardado en:  {pipeline_path}\n")
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error durante la transformación: {exc}", file=sys.stderr)
        return 1

