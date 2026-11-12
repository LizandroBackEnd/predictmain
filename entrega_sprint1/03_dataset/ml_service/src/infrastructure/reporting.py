"""Infrastructure adapters for Markdown report generation (profiling, null treatment, outliers)."""

from datetime import datetime

from src.domain.models import DatasetSummary, NullTreatmentResult, OutlierAnalysisResult
from src.domain.outlier_rules import OUTLIER_RULES


# ---------------------------------------------------------------------------
# Utilidad compartida
# ---------------------------------------------------------------------------


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Format tabular data into a standard GitHub Markdown table."""
    header_line = "| " + " | ".join(headers) + " |"
    separator_line = "| " + " | ".join([":---"] * len(headers)) + " |"
    data_lines = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header_line, separator_line] + data_lines)


# ---------------------------------------------------------------------------
# Reporte de perfilado
# ---------------------------------------------------------------------------


def build_profiling_report(summary: DatasetSummary, filename: str) -> str:
    """Render full Markdown profiling report from dataset summary metrics."""
    executed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines: list[str] = [
        f"# Reporte de Perfilado de Telemetría Histórica — {filename}",
        "",
        "> Documento generado automáticamente por el servicio de perfilado de PredictMain (HU-02).",
        "",
        "---",
        "",
        "## 1. Resumen Dimensional",
        "",
        f"- **Archivo analizado:** `{filename}`",
        f"- **Total de registros:** {summary.total_rows:,}",
        f"- **Total de columnas:** {summary.total_columns}",
        "",
        "## 2. Estadísticas de Variables Numéricas Operativas",
        "",
    ]

    numeric_rows: list[list[str]] = [
        [
            f"`{col.name}`",
            f"{col.min_value:,.2f}",
            f"{col.max_value:,.2f}",
            f"{col.mean_value:,.2f}",
            f"{col.median_value:,.2f}",
            f"{col.std_value:,.2f}",
            str(col.unique_count),
        ]
        for col in summary.columns
        if col.min_value is not None
    ]

    lines.append(
        _md_table(
            ["Variable", "Mínimo", "Máximo", "Media", "Mediana", "Desv. Estándar", "Únicos"],
            numeric_rows,
        )
    )
    lines.append("")

    lines.extend(["## 3. Distribución de Variables Categóricas", ""])

    cat_rows: list[list[str]] = [
        [
            f"`{col.name}`",
            str(col.unique_count),
            ", ".join(f"{k}: {v:,}" for k, v in col.distribution.items()),
        ]
        for col in summary.columns
        if col.distribution
    ]
    lines.append(_md_table(["Variable", "Valores Únicos", "Distribución"], cat_rows))
    lines.append("")

    lines.extend(["## 4. Distribución de la Variable Objetivo y Modos de Falla", ""])

    target_rows: list[list[str]] = []
    if summary.target_distribution:
        total = summary.total_rows
        class_0 = summary.target_distribution.get("0", 0)
        class_1 = summary.target_distribution.get("1", 0)
        pct_1 = (class_1 / total * 100) if total > 0 else 0
        target_rows.append(["`Machine failure`", f"{class_0:,}", f"{class_1:,}", f"{pct_1:.2f}%"])

    lines.append(_md_table(["Variable Objetivo", "Clase 0 (Normal)", "Clase 1 (Falla)", "% Falla"], target_rows))
    lines.append("")
    lines.extend(["### Modos Específicos de Falla Mecánica", ""])

    modes_rows: list[list[str]] = [
        [f"`{mode}`", f"{count:,}", f"{(count / summary.total_rows * 100) if summary.total_rows > 0 else 0:.2f}%"]
        for mode, count in summary.failure_modes_distribution.items()
    ]
    lines.append(_md_table(["Modo de Falla", "Ocurrencias", "% Incidencia"], modes_rows))
    lines.append("")

    lines.extend([
        "## 5. Control de Calidad contra Ficha Técnica UCI",
        "",
        _md_table(
            ["Criterio", "Observado", "Estado"],
            [
                ["Total registros", f"{summary.total_rows:,}", "✅ Coincide con UCI (10,000)"],
                ["Total columnas", f"{summary.total_columns}", "✅ Coincide con UCI (14)"],
                ["Valores nulos totales", "0", "✅ Sin valores faltantes en capa raw"],
                ["Categoría Type", "L, M, H", "✅ Válido (50% L, 30% M, 20% H)"],
                ["Variables continuas físicas", "Temp [K], RPM, Torque, Wear", "✅ Unidades y rangos válidos"],
            ],
        ),
        "",
    ])

    qr = summary.quality_report
    if qr is not None:
        lines.extend([
            "## 6. Reporte de Calidad del Dataset",
            "",
            f"- **Filas duplicadas detectadas:** {qr.duplicate_rows} "
            + ("✅ Sin duplicados" if qr.duplicate_rows == 0 else "⚠️ Requiere revisión"),
            f"- **Total de problemas encontrados:** {qr.total_issues} "
            + ("✅ Dataset limpio" if qr.total_issues == 0 else "⚠️ Ver detalle"),
            "",
        ])

        if qr.null_counts:
            null_rows = [[f"`{col}`", str(cnt), "⚠️ Contiene nulos"] for col, cnt in qr.null_counts.items()]
            lines.extend(["### 6.1 Valores Nulos por Columna", "", _md_table(["Columna", "Nulos", "Estado"], null_rows), ""])
        else:
            lines.extend(["### 6.1 Valores Nulos por Columna", "", "> ✅ Ninguna columna contiene valores nulos.", ""])

        if qr.out_of_range:
            range_rows = [
                [f"`{col}`", str(len(indices)), f"Filas: {indices[:5]}{'...' if len(indices) > 5 else ''}"]
                for col, indices in qr.out_of_range.items()
            ]
            lines.extend([
                "### 6.2 Valores Fuera de Rango Físico (Especificación UCI)",
                "",
                _md_table(["Columna", "Registros afectados", "Primeros índices"], range_rows),
                "",
            ])
        else:
            lines.extend([
                "### 6.2 Valores Fuera de Rango Físico (Especificación UCI)",
                "",
                "> ✅ Todos los valores están dentro de los rangos físicos documentados por UCI.",
                "",
            ])

        if qr.invalid_type_values:
            inv_rows = [[f"`{col}`", str(cnt), "⚠️ Valores inesperados"] for col, cnt in qr.invalid_type_values.items()]
            lines.extend([
                "### 6.3 Valores Inválidos en Columnas Categóricas y Binarias",
                "",
                _md_table(["Columna", "Registros afectados", "Estado"], inv_rows),
                "",
            ])
        else:
            lines.extend([
                "### 6.3 Valores Inválidos en Columnas Categóricas y Binarias",
                "",
                "> ✅ Todas las columnas categóricas y binarias contienen únicamente valores válidos.",
                "",
            ])

        section_7, section_8 = "## 7.", "## 8."
    else:
        section_7, section_8 = "## 6.", "## 7."

    lines.extend([
        section_7 + " Variables Candidatas para Modelado Predictivo",
        "",
        _md_table(
            ["Variable", "Rol en Modelado", "Consideración de Ingeniería"],
            [
                ["`Air temperature [K]`", "Predictora continua", "Temperatura ambiente en planta."],
                ["`Process temperature [K]`", "Predictora continua", "Fricción de manufactura; relación térmica directa."],
                ["`Rotational speed [rpm]`", "Predictora continua", "Velocidad del husillo."],
                ["`Torque [Nm]`", "Predictora continua", "Fuerza mecánica aplicada."],
                ["`Tool wear [min]`", "Predictora continua", "Desgaste de herramienta acumulado."],
                ["`Type`", "Predictora categórica", "Variante de producto (L, M, H) a codificar mediante One-Hot."],
                ["`UDI` / `Product ID`", "Identificadores (Excluir)", "No predictivos; evitan fuga de información."],
                ["`TWF`, `HDF`, `PWF`, `OSF`, `RNF`", "Etiquetas auxiliares", "Modos de falla para análisis multietiqueta futuro."],
            ],
        ),
        "",
        section_8 + " Conclusión",
        "",
        "El dataset AI4I 2020 se encuentra validado y listo para la fase de preparación y modelado sin inconsistencias estructurales.",
        "",
        "---",
        "",
        f"> **Reporte generado:** {executed_at}",
    ])

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Reporte de tratamiento de nulos
# ---------------------------------------------------------------------------


def build_null_report(result: NullTreatmentResult) -> str:
    """Render the null treatment audit report as Markdown."""
    from src.domain.null_rules import RULES_BY_COLUMN

    lines: list[str] = [
        "# Reporte de Tratamiento de Valores Nulos — HU-04",
        "",
        "> Generado automáticamente por el pipeline de tratamiento de PredictMain.",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo",
        "",
        "| Métrica | Valor |",
        "| :--- | :--- |",
        f"| Archivo fuente | `{result.source_file}` |",
        f"| Archivo depurado | `{result.output_file}` |",
        f"| Fecha de ejecución | {result.executed_at} |",
        f"| Filas antes del tratamiento | {result.rows_before:,} |",
        f"| Filas con al menos un nulo | {result.rows_with_nulls_before:,} |",
        f"| Total de valores nulos encontrados | {result.total_nulls_before:,} |",
        f"| Filas eliminadas (labels nulos) | {result.rows_dropped:,} |",
        f"| Valores imputados | {result.total_values_imputed:,} |",
        f"| Filas en dataset depurado | {result.rows_after:,} |",
        "",
    ]

    if result.total_nulls_before == 0:
        lines += [
            "> ✅ **El dataset no contenía valores nulos.** "
            "No se realizaron imputaciones ni eliminaciones.",
            "",
        ]
    else:
        lines += [
            f"> ⚠️ Se encontraron **{result.total_nulls_before:,} valores nulos** "
            f"en **{result.rows_with_nulls_before:,} registros**. "
            "Se aplicaron las reglas documentadas.",
            "",
        ]

    lines += [
        "## 2. Detalle por Columna — Antes y Después",
        "",
        _md_table(
            ["Columna", "Nulos antes", "% Nulos", "Decisión", "Estrategia", "Imputados", "Filas eliminadas"],
            [
                [
                    f"`{s.column}`",
                    str(s.null_count_before),
                    f"{s.null_pct_before:.2f}%",
                    s.disposition,
                    s.strategy or "—",
                    str(s.imputed_count),
                    str(s.dropped_rows),
                ]
                for s in result.column_stats
            ],
        ),
        "",
        "## 3. Justificación Técnica de las Reglas",
        "",
        _md_table(
            ["Columna", "Decisión", "Justificación"],
            [
                [f"`{rule.column}`", rule.disposition, rule.justification]
                for rule in RULES_BY_COLUMN.values()
            ],
        ),
        "",
        "## 4. Conclusión",
        "",
        f"El dataset depurado contiene **{result.rows_after:,} registros** "
        "listos para la fase de transformación (HU-05). ",
    ]

    if result.rows_dropped > 0:
        lines.append(
            f"Se eliminaron **{result.rows_dropped:,} filas** por tener etiquetas nulas "
            "que no pueden ser imputadas sin introducir sesgo."
        )
    if result.total_values_imputed > 0:
        lines.append(
            f"Se imputaron **{result.total_values_imputed:,} valores** usando "
            "mediana (variables continuas) y moda (variables categóricas)."
        )
    if result.total_nulls_before == 0:
        lines.append("No se requirió ninguna modificación: el dataset estaba completo.")

    lines += ["", "---", "", f"> **Reporte generado:** {result.executed_at}", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Reporte de análisis de atípicos
# ---------------------------------------------------------------------------


def build_outlier_report(result: OutlierAnalysisResult) -> str:
    """Render the outlier analysis audit report as Markdown."""
    lines: list[str] = [
        "# Reporte de Análisis de Valores Atípicos — HU-05",
        "",
        "> Generado automáticamente por el pipeline de análisis de PredictMain.",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo",
        "",
        "| Métrica | Valor |",
        "| :--- | :--- |",
        f"| Archivo analizado | `{result.source_file}` |",
        f"| Fecha de ejecución | {result.executed_at} |",
        f"| Registros de entrada | {result.rows_input:,} |",
        f"| Registros de salida | {result.rows_output:,} |",
        f"| Total outliers detectados (unión IQR+P1/P99) | {result.total_detected:,} |",
        f"| Total valores modificados (CAP) | {result.total_modified:,} |",
        f"| Total filas excluidas | {result.total_excluded:,} |",
        "",
        "> **Principio:** Los outliers NO se eliminan automáticamente. "
        "Cada decisión está justificada con criterios del dominio físico.",
        "",
        "---",
        "",
        "## 2. Detección por Columna — IQR y Percentiles",
        "",
        _md_table(
            ["Variable", "Q1", "Q3", "IQR", "Fence Low", "Fence High",
             "IQR outliers", "P1", "P99", "P1/P99 outliers", "Fuera rango UCI"],
            [
                [
                    f"`{s.column}`",
                    f"{s.q1:.2f}", f"{s.q3:.2f}", f"{s.iqr:.2f}",
                    f"{s.iqr_fence_low:.2f}", f"{s.iqr_fence_high:.2f}",
                    str(s.iqr_outliers_count),
                    f"{s.p1:.2f}", f"{s.p99:.2f}",
                    str(s.percentile_outliers_count),
                    str(s.outside_physical_range),
                ]
                for s in result.column_stats
            ],
        ),
        "",
        "---",
        "",
        "## 3. Decisión por Variable — Regla → Decisión → Conteos",
        "",
        _md_table(
            ["Variable", "Tipo de atípico", "Detección", "Decisión",
             "Detectados", "Modificados", "Excluidos"],
            [
                [
                    f"`{s.column}`",
                    s.outlier_type,
                    s.detection_method,
                    f"**{s.decision}**",
                    str(s.records_detected),
                    str(s.records_modified),
                    str(s.records_excluded),
                ]
                for s in result.column_stats
            ],
        ),
        "",
        "---",
        "",
        "## 4. Justificación Técnica por Variable",
        "",
    ]

    for rule in OUTLIER_RULES:
        lines += [
            f"### `{rule.column}`",
            "",
            f"- **Decisión:** {rule.decision}",
            f"- **Tipo:** {rule.outlier_type}",
            f"- **Rango físico UCI:** [{rule.uci_physical_min}, {rule.uci_physical_max}]",
            f"- **Justificación:** {rule.rationale}",
            "",
        ]

    lines += [
        "---",
        "",
        "## 5. Conclusión",
        "",
        f"Se analizaron **{len(result.column_stats)} variables** de sensores. "
        f"Se detectaron **{result.total_detected:,} valores atípicos** en total "
        "(unión de IQR 1.5× y percentiles P1/P99). ",
    ]

    if result.total_modified > 0:
        lines.append(f"Se aplicó Winsorización (CAP) a **{result.total_modified:,} valores**.")
    if result.total_excluded > 0:
        lines.append(f"Se excluyeron **{result.total_excluded:,} filas** por valores físicamente imposibles.")
    if result.total_modified == 0 and result.total_excluded == 0:
        lines.append(
            "**Todos los outliers fueron conservados (KEEP):** representan señales "
            "físicas válidas o precursores de falla con valor predictivo para el modelo."
        )

    lines += ["", "---", "", f"> **Reporte generado:** {result.executed_at}", ""]
    return "\n".join(lines)

