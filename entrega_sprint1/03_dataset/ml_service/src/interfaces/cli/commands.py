"""Command handlers for PredictMain data & ML CLI."""

from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.application.dataset_split import split_dataset
from src.application.ingestion import IngestionService
from src.application.matrix_validation import validate_feature_matrix
from src.application.null_treatment import NullTreatmentService
from src.application.outlier_analysis import OutlierAnalysisService
from src.application.profiling import ProfilingService
from src.application.transformation import TransformationService
from src.domain.models import TransformationRunResult
from src.infrastructure.paths import paths
from src.infrastructure.reporting import (
    build_matrix_validation_report,
    build_transformation_report,
)


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


def run_transform_cmd(
    csv_path: Path,
    output_csv: Path,
    pipeline_path: Path,
    report_path: Path,
) -> int:
    """Fit the pipeline on train only, transform test and serialize it (HU-06)."""
    print("=" * 60)
    print("⚙️  PredictMain — HU-06: Pipeline de Transformación")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Salida CSV:     {output_csv}")
    print(f"Pipeline:       {pipeline_path}")
    print(f"Reporte:        {report_path}\n")

    service = TransformationService()
    try:
        df = pd.read_csv(csv_path)
        split = split_dataset(df)
        X_train, _ = service.split_features_target(split.train)
        X_test, _ = service.split_features_target(split.test)

        X_train_transformed = service.fit_transform(X_train)
        X_test_transformed = service.transform(X_test)

        missing = service.verify_output(X_train_transformed)
        if missing:
            print(f"❌ Columnas faltantes en la salida: {missing}", file=sys.stderr)
            return 1
        if list(X_test_transformed.columns) != list(X_train_transformed.columns):
            print("❌ El conjunto de prueba produjo columnas distintas.", file=sys.stderr)
            return 1

        service.save(pipeline_path)

        X, y = service.split_features_target(df)
        X_transformed = service.transform(X)
        out_df = X_transformed.copy()
        if not y.empty:
            out_df[y.name] = y.values
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_csv, index=False)

        try:
            pipeline_label = str(pipeline_path.relative_to(paths.root))
        except ValueError:
            pipeline_label = str(pipeline_path)

        result = TransformationRunResult(
            source_file=csv_path.name,
            executed_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            rows_input=len(df),
            train_rows=split.train_rows,
            test_rows=split.test_rows,
            test_size=split.test_size,
            random_state=split.random_state,
            stratified=split.stratified,
            feature_columns=list(X_transformed.columns),
            excluded_columns=[c for c in df.columns if c not in X.columns],
            target_column=y.name if not y.empty else "",
            rows_output=len(out_df),
            null_count=int(X_transformed.isna().sum().sum()),
            pipeline_path=pipeline_label,
        )
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            build_transformation_report(result), encoding="utf-8"
        )

        print("✅ Pipeline ajustado solo con entrenamiento y guardado.")
        print(f"• Filas de entrenamiento (fit): {split.train_rows:,}")
        print(f"• Filas de prueba (transform):  {split.test_rows:,}")
        print(f"• Filas transformadas:         {len(X_transformed):,}")
        print(f"• Columnas de features:        {len(X_transformed.columns)}")
        print(f"• Columnas: {list(X_transformed.columns)}")
        print(f"• Pipeline guardado en:        {pipeline_path}")
        print(f"• Reporte guardado en:         {report_path}\n")
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error durante la transformación: {exc}", file=sys.stderr)
        return 1


def run_apply_cmd(csv_path: Path, output_csv: Path, pipeline_path: Path) -> int:
    """Apply the saved pipeline to new data without re-fitting (HU-06)."""
    print("=" * 60)
    print("🚀 PredictMain — HU-06: Aplicar pipeline a datos nuevos")
    print("=" * 60)
    print(f"Datos nuevos:   {csv_path}")
    print(f"Salida CSV:     {output_csv}")
    print(f"Pipeline:       {pipeline_path}\n")

    service = TransformationService()
    try:
        service.load(pipeline_path)
        df = pd.read_csv(csv_path)
        X, y = service.split_features_target(df)
        X_transformed = service.transform(X)

        missing = service.verify_output(X_transformed)
        if missing:
            print(f"❌ Columnas faltantes en la salida: {missing}", file=sys.stderr)
            return 1

        out_df = X_transformed.copy()
        if not y.empty:
            out_df[y.name] = y.values
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        out_df.to_csv(output_csv, index=False)

        print("✅ Pipeline cargado y aplicado sin re-ajuste.")
        print(f"• Filas transformadas:  {len(X_transformed):,}")
        print(f"• Columnas de features: {len(X_transformed.columns)}")
        print(f"• Salida: {output_csv}\n")
        return 0
    except (RuntimeError, ValueError, OSError) as exc:
        print(f"❌ Error al aplicar el pipeline: {exc}", file=sys.stderr)
        return 1


def run_validate_cmd(
    csv_path: Path,
    matrix_csv_path: Path,
    report_path: Path,
) -> int:
    """Validate the final matrix, export X without y and write the report."""
    print("=" * 60)
    print("🔍 PredictMain — HU-07: Validar matriz de características")
    print("=" * 60)
    print(f"Dataset CSV:    {csv_path}")
    print(f"Matriz CSV:     {matrix_csv_path}")
    print(f"Reporte:        {report_path}\n")

    try:
        df = pd.read_csv(csv_path)
        X, y = TransformationService.split_features_target(df)
        result = validate_feature_matrix(
            X,
            y if not y.empty else None,
            source_file=csv_path.name,
        )

        matrix_csv_path.parent.mkdir(parents=True, exist_ok=True)
        X.to_csv(matrix_csv_path, index=False)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            build_matrix_validation_report(result), encoding="utf-8"
        )

        for check in result.checks:
            mark = "✔" if check.passed else "✘"
            print(f"• {mark} [{check.criterion}] {check.name}: {check.detail}")
        print(f"• Shape X: {result.x_shape}; Shape y: {result.y_shape}")
        print(f"• Matriz guardada en: {matrix_csv_path}")
        print(f"• Reporte guardado en: {report_path}\n")
        return 0 if result.passed else 1
    except (ValueError, OSError) as exc:
        print(f"❌ Error durante la validación: {exc}", file=sys.stderr)
        return 1

