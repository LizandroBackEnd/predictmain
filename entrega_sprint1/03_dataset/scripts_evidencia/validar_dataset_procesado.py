"""Valida el dataset procesado y los artefactos del pipeline PredictMain."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
REPORTS = ROOT / "reports"
ARTIFACTS = ROOT / "ml_service" / "artifacts"
OUTPUT = ROOT / "evidencias" / "validacion_dataset.md"

EXPECTED_FEATURES = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Temp_diff",
    "Type_L",
    "Type_M",
]
FAILURE_MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        results.append((name, condition, detail))

    raw = pd.read_csv(RAW / "ai4i2020.csv")
    clean = pd.read_csv(PROCESSED / "ai4i2020_clean.csv")
    analyzed = pd.read_csv(PROCESSED / "ai4i2020_outlier_analyzed.csv")
    transformed = pd.read_csv(PROCESSED / "ai4i2020_transformed.csv")

    check("Dataset crudo con 10.000 filas y 14 columnas", raw.shape == (10000, 14), f"{raw.shape}")
    check("Dataset limpio conserva 10.000 filas y 14 columnas", clean.shape == (10000, 14), f"{clean.shape}")
    check("Dataset de atípicos conserva 10.000 filas y 14 columnas", analyzed.shape == (10000, 14), f"{analyzed.shape}")
    check("Dataset transformado con 10.000 filas y 9 columnas", transformed.shape == (10000, 9), f"{transformed.shape}")

    check("Sin nulos en el dataset crudo", int(raw.isna().sum().sum()) == 0, "0 nulos")
    check("Sin nulos en el dataset limpio", int(clean.isna().sum().sum()) == 0, "0 nulos")
    check("Sin nulos en el dataset de atípicos", int(analyzed.isna().sum().sum()) == 0, "0 nulos")
    check("Sin nulos en el dataset transformado", int(transformed.isna().sum().sum()) == 0, "0 nulos")
    check("Sin duplicados en el dataset crudo", int(raw.duplicated().sum()) == 0, "0 duplicados")

    check("Variable objetivo binaria", set(raw["Machine failure"].unique()) <= {0, 1}, "valores 0 y 1")
    check("Total de fallas igual a 339", int(raw["Machine failure"].sum()) == 339, f"{int(raw['Machine failure'].sum())} fallas")
    check(
        "Tipos de producto válidos",
        set(raw["Type"].unique()) <= {"L", "M", "H"},
        str(sorted(raw["Type"].unique())),
    )
    check(
        "Modos de falla binarios",
        all(set(raw[mode].unique()) <= {0, 1} for mode in FAILURE_MODES),
        ", ".join(FAILURE_MODES),
    )

    check(
        "Columnas de entrada del modelo correctas",
        list(transformed.columns[:-1]) == EXPECTED_FEATURES,
        ", ".join(transformed.columns[:-1]),
    )
    check(
        "Etiqueta objetivo al final del dataset transformado",
        transformed.columns[-1] == "Machine failure",
        transformed.columns[-1],
    )
    check(
        "Etiqueta objetivo preservada",
        bool((transformed["Machine failure"].values == raw["Machine failure"].values).all()),
        f"{int(transformed['Machine failure'].sum())} fallas",
    )

    manifest_path = RAW / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    actual_hash = _sha256(RAW / "ai4i2020.csv")
    check("Manifiesto declara 10.000 filas", manifest.get("n_rows") == 10000, str(manifest.get("n_rows")))
    check("Manifiesto declara 14 columnas", manifest.get("n_columns") == 14, str(manifest.get("n_columns")))
    check("Hash del manifiesto coincide con el CSV", manifest.get("sha256") == actual_hash, actual_hash[:16] + "...")

    check("Artefacto del pipeline existe", (ARTIFACTS / "pipeline.joblib").is_file(), "pipeline.joblib")
    check("Reporte de nulos existe", (REPORTS / "null_report.md").is_file(), "null_report.md")
    check("Reporte de atípicos existe", (REPORTS / "outlier_report.md").is_file(), "outlier_report.md")

    lines: list[str] = [
        "# Validación del dataset procesado",
        "",
        "Generado automáticamente por `scripts_evidencia/validar_dataset_procesado.py`.",
        "",
        _md_table(
            ["Verificación", "Resultado", "Detalle"],
            [[name, "OK" if ok else "FALLA", detail] for name, ok, detail in results],
        ),
        "",
    ]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Validación generada en: {OUTPUT}")

    failures = [name for name, ok, _ in results if not ok]
    if failures:
        print("Verificaciones fallidas:")
        for name in failures:
            print(f"- {name}")
        return 1
    print(f"Todas las verificaciones pasaron ({len(results)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
