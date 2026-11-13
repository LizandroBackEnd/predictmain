"""Genera una comparativa de los datasets del pipeline PredictMain."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "evidencias" / "comparativa_datasets.md"

NUMERIC_FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]
# Column changes that the pipeline documents in documentacion/limpieza_transformacion.md.
INTENTIONAL_COLUMN_CHANGES = {
    "Temp_diff": "Variable derivada `Process temperature - Air temperature` (HU-06, sección 3.5).",
    "Type_L": "One-Hot Encoding de `Type` (HU-06, sección 3.5).",
    "Type_M": "One-Hot Encoding de `Type` (HU-06, sección 3.5).",
    "Type": "Reemplazada por `Type_L` y `Type_M`; `Type_H` es la categoría de referencia (HU-06).",
    "UDI": "Identificador no predictivo excluido de las variables de entrada (HU-06).",
    "Product ID": "Identificador no predictivo excluido de las variables de entrada (HU-06).",
    "TWF": "Modo de falla excluido para evitar fuga de información (HU-06).",
    "HDF": "Modo de falla excluido para evitar fuga de información (HU-06).",
    "PWF": "Modo de falla excluido para evitar fuga de información (HU-06).",
    "OSF": "Modo de falla excluido para evitar fuga de información (HU-06).",
    "RNF": "Modo de falla excluido para evitar fuga de información (HU-06).",
}


def _md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _summary(name: str, path: Path) -> dict[str, object]:
    df = pd.read_csv(path)
    return {
        "nombre": name,
        "archivo": path.name,
        "filas": len(df),
        "columnas": len(df.columns),
        "nulos": int(df.isna().sum().sum()),
        "duplicados": int(df.duplicated().sum()),
        "fallas": int(df["Machine failure"].sum()) if "Machine failure" in df.columns else "N/A",
        "columnas_lista": ", ".join(df.columns),
    }


def _same_values(left: pd.Series, right: pd.Series) -> bool:
    return len(left) == len(right) and bool((left.values == right.values).all())


def _changed_cells(before: pd.DataFrame, after: pd.DataFrame) -> int:
    if before.shape != after.shape or list(before.columns) != list(after.columns):
        return -1
    return int((before.ne(after) & ~(before.isna() & after.isna())).sum().sum())


def _column_changes(stages: list[tuple[str, pd.DataFrame]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for (previous_name, previous), (name, current) in zip(stages, stages[1:]):
        added = [column for column in current.columns if column not in previous.columns]
        removed = [column for column in previous.columns if column not in current.columns]
        for change, columns in (("Agregada", added), ("Eliminada", removed)):
            for column in columns:
                reason = INTENTIONAL_COLUMN_CHANGES.get(column)
                rows.append([
                    f"{previous_name} → {name}",
                    change,
                    f"`{column}`",
                    "Sí" if reason else "No",
                    reason or "Cambio no documentado",
                ])
        if not added and not removed:
            rows.append([f"{previous_name} → {name}", "Sin cambios", "-", "Sí", "Esquema conservado"])
    return rows


def main() -> int:
    datasets = [
        ("Crudo", DATA / "raw" / "ai4i2020.csv"),
        ("Limpio (HU-04)", DATA / "processed" / "ai4i2020_clean.csv"),
        ("Atípicos analizados (HU-05)", DATA / "processed" / "ai4i2020_outlier_analyzed.csv"),
        ("Transformado (HU-06)", DATA / "processed" / "ai4i2020_transformed.csv"),
    ]
    missing = [path for _, path in datasets if not path.is_file() or path.stat().st_size == 0]
    if missing:
        for path in missing:
            print(f"Entrada faltante o vacía: {path}", file=sys.stderr)
        print("No se generó la comparativa.", file=sys.stderr)
        return 1

    summaries = [_summary(name, path) for name, path in datasets]

    raw = pd.read_csv(datasets[0][1])
    clean = pd.read_csv(datasets[1][1])
    outlier = pd.read_csv(datasets[2][1])
    transformed = pd.read_csv(datasets[3][1])

    checks: list[list[object]] = []
    checks.append([
        "Filas conservadas en limpieza",
        len(clean) == len(raw),
        f"{len(clean):,} de {len(raw):,}",
    ])
    checks.append([
        "Columnas conservadas en limpieza",
        list(clean.columns) == list(raw.columns),
        f"{len(clean.columns)} columnas",
    ])
    checks.append([
        "Etiqueta objetivo idéntica tras limpieza",
        _same_values(clean["Machine failure"], raw["Machine failure"]),
        f"{int(clean['Machine failure'].sum()):,} fallas",
    ])
    checks.append([
        "Filas conservadas tras análisis de atípicos",
        len(outlier) == len(clean),
        f"{len(outlier):,} de {len(clean):,}",
    ])
    checks.append([
        "Filas conservadas tras transformación",
        len(transformed) == len(outlier),
        f"{len(transformed):,} de {len(outlier):,}",
    ])
    checks.append([
        "Etiqueta objetivo idéntica tras transformación",
        _same_values(transformed["Machine failure"], raw["Machine failure"]),
        f"{int(transformed['Machine failure'].sum()):,} fallas",
    ])
    expected_features = [
        "Air temperature [K]",
        "Process temperature [K]",
        "Rotational speed [rpm]",
        "Torque [Nm]",
        "Tool wear [min]",
        "Temp_diff",
        "Type_L",
        "Type_M",
    ]
    checks.append([
        "Variables de entrada del modelo",
        list(transformed.columns[:-1]) == expected_features,
        f"{len(transformed.columns) - 1} variables",
    ])
    checks.append([
        "Sin valores nulos en la salida",
        int(transformed.isna().sum().sum()) == 0,
        "0 nulos",
    ])
    column_changes = _column_changes([(name, frame) for (name, _), frame in zip(datasets, [raw, clean, outlier, transformed])])
    undocumented = [row for row in column_changes if row[3] == "No"]
    checks.append([
        "Todos los cambios de columnas son intencionales",
        not undocumented,
        f"{len(undocumented)} cambios no documentados",
    ])
    cells_clean = _changed_cells(raw, clean)
    cells_outlier = _changed_cells(clean, outlier)
    checks.append(["Valores sin modificar en limpieza", cells_clean == 0, f"{cells_clean} celdas modificadas"])
    checks.append(["Valores sin modificar en análisis de atípicos", cells_outlier == 0, f"{cells_outlier} celdas modificadas"])

    representative_rows: list[list[object]] = []
    for feature in NUMERIC_FEATURES + ["Temp_diff"]:
        source = raw[feature] if feature in raw.columns else raw["Process temperature [K]"] - raw["Air temperature [K]"]
        representative_rows.append([
            f"`{feature}`",
            f"{source.mean():.3f}",
            f"{source.std():.3f}",
            f"{source.min():.3f} / {source.max():.3f}",
            f"{transformed[feature].mean():.3f}",
            f"{transformed[feature].std():.3f}",
        ])

    type_counts = raw["Type"].value_counts().reindex(["L", "M", "H"]).fillna(0).astype(int)
    modes = {mode: int(raw[mode].sum()) for mode in ["TWF", "HDF", "PWF", "OSF", "RNF"]}

    lines: list[str] = [
        "# Comparativa de datasets del pipeline",
        "",
        "Generado automáticamente por `scripts_evidencia/comparar_datasets.py`.",
        "",
        "## 1. Resumen por etapa",
        "",
        _md_table(
            ["Etapa", "Archivo", "Filas", "Columnas", "Nulos", "Duplicados", "Fallas"],
            [
                [s["nombre"], s["archivo"], f"{s['filas']:,}", s["columnas"], s["nulos"], s["duplicados"], s["fallas"]]
                for s in summaries
            ],
        ),
        "",
        "## 2. Verificaciones de integridad",
        "",
        _md_table(["Verificación", "Resultado", "Detalle"], [
            [name, "OK" if ok else "FALLA", detail] for name, ok, detail in checks
        ]),
        "",
        "## 3. Distribución de la variable objetivo",
        "",
        _md_table(
            ["Clase", "Registros", "Porcentaje"],
            [
                ["0 (sin falla)", f"{int((raw['Machine failure'] == 0).sum()):,}", f"{(raw['Machine failure'] == 0).mean() * 100:.2f}%"],
                ["1 (falla)", f"{int((raw['Machine failure'] == 1).sum()):,}", f"{(raw['Machine failure'] == 1).mean() * 100:.2f}%"],
            ],
        ),
        "",
        "## 4. Distribución por tipo de producto",
        "",
        _md_table(
            ["Tipo", "Registros", "Porcentaje"],
            [[t, f"{int(type_counts[t]):,}", f"{type_counts[t] / len(raw) * 100:.2f}%"] for t in ["L", "M", "H"]],
        ),
        "",
        "## 5. Modos de falla registrados",
        "",
        _md_table(
            ["Modo", "Registros"],
            [[mode, f"{count:,}"] for mode, count in modes.items()],
        ),
        "",
        "> Los modos de falla pueden solaparse en un mismo registro; por eso su suma puede superar el total de fallas.",
        "",
        "## 6. Columnas por etapa",
        "",
    ]
    for summary in summaries:
        lines.extend([f"### {summary['nombre']}", "", f"`{summary['columnas_lista']}`", ""])
    lines.extend([
        "## 7. Cambios de columnas entre etapas",
        "",
        _md_table(["Etapas", "Cambio", "Columna", "Intencional", "Justificación"], column_changes),
        "",
        "## 8. Valores representativos (crudo frente a transformado)",
        "",
        "El dataset transformado estandariza las variables numéricas; por eso su media es cercana a 0 y su desviación estándar a 1.",
        "`Temp_diff` se calcula sobre el crudo para comparar la variable derivada.",
        "",
        _md_table(
            ["Variable", "Media cruda", "Desv. cruda", "Mín. / Máx. crudo", "Media transformada", "Desv. transformada"],
            representative_rows,
        ),
        "",
        "## 9. Cambios intencionales por etapa",
        "",
        f"- Limpieza (HU-04): {cells_clean} celdas modificadas y 0 filas eliminadas; no había nulos que imputar.",
        f"- Análisis de atípicos (HU-05): {cells_outlier} celdas modificadas; los atípicos se conservan y solo se documentan.",
        "- Transformación (HU-06): estandarización de variables numéricas, `Temp_diff` derivada, One-Hot de `Type` y exclusión de identificadores y modos de falla.",
        "- La etiqueta `Machine failure` se conserva sin cambios en todas las etapas.",
        "",
    ])

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Comparativa generada en: {OUTPUT}")
    failed = [name for name, ok, _ in checks if not ok]
    if failed:
        print("Verificaciones fallidas: " + ", ".join(failed))
        return 1
    print("Todas las verificaciones de integridad pasaron.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
