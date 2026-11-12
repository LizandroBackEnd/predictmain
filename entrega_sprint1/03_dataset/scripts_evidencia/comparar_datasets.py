"""Genera una comparativa de los datasets del pipeline PredictMain."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUTPUT = ROOT / "evidencias" / "comparativa_datasets.md"


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


def main() -> int:
    datasets = [
        ("Crudo", DATA / "raw" / "ai4i2020.csv"),
        ("Limpio (HU-04)", DATA / "processed" / "ai4i2020_clean.csv"),
        ("Atípicos analizados (HU-05)", DATA / "processed" / "ai4i2020_outlier_analyzed.csv"),
        ("Transformado (HU-06)", DATA / "processed" / "ai4i2020_transformed.csv"),
    ]
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
        bool((clean["Machine failure"].values == raw["Machine failure"].values).all()),
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
        bool((transformed["Machine failure"].values == raw["Machine failure"].values).all()),
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
