"""Valida el dataset procesado y los artefactos del pipeline PredictMain."""

from __future__ import annotations

import hashlib
import json
import sys
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
EXPECTED_RAW_SHA256 = "59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183"
EXPECTED_RAW_COLUMNS = [
    "UDI",
    "Product ID",
    "Type",
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
    "Machine failure",
    "TWF",
    "HDF",
    "PWF",
    "OSF",
    "RNF",
]
FAILURE_MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]
EXPECTED_TARGET_DISTRIBUTION = {0: 9661, 1: 339}
EXPECTED_TYPE_DISTRIBUTION = {"L": 6000, "M": 2997, "H": 1003}
INPUTS = {
    "raw": RAW / "ai4i2020.csv",
    "manifest": RAW / "manifest.json",
    "clean": PROCESSED / "ai4i2020_clean.csv",
    "analyzed": PROCESSED / "ai4i2020_outlier_analyzed.csv",
    "transformed": PROCESSED / "ai4i2020_transformed.csv",
}
GENERATED_OUTPUTS = [
    ARTIFACTS / "pipeline.joblib",
    REPORTS / "null_report.md",
    REPORTS / "outlier_report.md",
]


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


def _distribution(series: pd.Series) -> dict[object, int]:
    return {key: int(value) for key, value in series.value_counts().sort_index().items()}


def main() -> int:
    missing = [path for path in INPUTS.values() if not path.is_file() or path.stat().st_size == 0]
    if missing:
        for path in missing:
            print(f"Entrada faltante o vacía: {path}", file=sys.stderr)
        print("No se generó el reporte de validación.", file=sys.stderr)
        return 1

    results: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        results.append((name, condition, detail))

    raw = pd.read_csv(INPUTS["raw"])
    clean = pd.read_csv(INPUTS["clean"])
    analyzed = pd.read_csv(INPUTS["analyzed"])
    transformed = pd.read_csv(INPUTS["transformed"])

    check("Dataset crudo con 10.000 filas y 14 columnas", raw.shape == (10000, 14), f"{raw.shape}")
    check("Esquema canónico del dataset crudo", list(raw.columns) == EXPECTED_RAW_COLUMNS, ", ".join(raw.columns))
    check("Dataset limpio conserva 10.000 filas y 14 columnas", clean.shape == (10000, 14), f"{clean.shape}")
    check("Esquema del dataset limpio igual al crudo", list(clean.columns) == EXPECTED_RAW_COLUMNS, f"{len(clean.columns)} columnas")
    check("Dataset de atípicos conserva 10.000 filas y 14 columnas", analyzed.shape == (10000, 14), f"{analyzed.shape}")
    check("Esquema del dataset de atípicos igual al crudo", list(analyzed.columns) == EXPECTED_RAW_COLUMNS, f"{len(analyzed.columns)} columnas")
    check("Dataset transformado con 10.000 filas y 9 columnas", transformed.shape == (10000, 9), f"{transformed.shape}")

    # Zero findings are reported as executed checks with an explicit count of 0.
    for label, frame in (("crudo", raw), ("limpio", clean), ("de atípicos", analyzed), ("transformado", transformed)):
        nulls = int(frame.isna().sum().sum())
        check(f"Sin nulos en el dataset {label}", nulls == 0, f"ejecutada: {nulls} nulos")
    for label, frame in (("crudo", raw), ("limpio", clean)):
        duplicates = int(frame.duplicated().sum())
        check(f"Sin duplicados en el dataset {label}", duplicates == 0, f"ejecutada: {duplicates} duplicados")

    check("Variable objetivo binaria", set(raw["Machine failure"].unique()) <= {0, 1}, "valores 0 y 1")
    check("Total de fallas igual a 339", int(raw["Machine failure"].sum()) == 339, f"{int(raw['Machine failure'].sum())} fallas")
    for label, frame in (("crudo", raw), ("limpio", clean), ("de atípicos", analyzed), ("transformado", transformed)):
        distribution = _distribution(frame["Machine failure"])
        check(
            f"Distribución objetivo esperada en el dataset {label}",
            distribution == EXPECTED_TARGET_DISTRIBUTION,
            f"{distribution}",
        )
    for label, frame in (("crudo", raw), ("limpio", clean), ("de atípicos", analyzed)):
        check(
            f"Tipos de producto válidos en el dataset {label}",
            set(frame["Type"].unique()) <= {"L", "M", "H"},
            str(sorted(frame["Type"].unique())),
        )
    type_distribution = {key: int(raw["Type"].eq(key).sum()) for key in EXPECTED_TYPE_DISTRIBUTION}
    check(
        "Distribución de tipos de producto esperada",
        type_distribution == EXPECTED_TYPE_DISTRIBUTION,
        f"{type_distribution}",
    )
    one_hot = {"Type_L": int(transformed["Type_L"].sum()), "Type_M": int(transformed["Type_M"].sum())}
    check(
        "Codificación one-hot coincide con `Type`",
        set(transformed["Type_L"].unique()) <= {0, 1}
        and set(transformed["Type_M"].unique()) <= {0, 1}
        and one_hot == {"Type_L": type_distribution["L"], "Type_M": type_distribution["M"]},
        f"{one_hot}",
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
        len(transformed) == len(raw)
        and bool((transformed["Machine failure"].values == raw["Machine failure"].values).all()),
        f"{int(transformed['Machine failure'].sum())} fallas",
    )

    manifest = json.loads(INPUTS["manifest"].read_text(encoding="utf-8"))
    actual_hash = _sha256(INPUTS["raw"])
    check("Manifiesto declara 10.000 filas", manifest.get("n_rows") == 10000, str(manifest.get("n_rows")))
    check("Manifiesto declara 14 columnas", manifest.get("n_columns") == 14, str(manifest.get("n_columns")))
    check("Hash del manifiesto coincide con el CSV", manifest.get("sha256") == actual_hash, actual_hash[:16] + "...")
    check("Hash del CSV coincide con la fuente canónica", actual_hash == EXPECTED_RAW_SHA256, actual_hash)
    check(
        "Manifiesto coincide con la fuente canónica",
        manifest.get("sha256") == EXPECTED_RAW_SHA256,
        str(manifest.get("sha256")),
    )

    check("Artefacto del pipeline existe", (ARTIFACTS / "pipeline.joblib").is_file(), "pipeline.joblib")
    check("Reporte de nulos existe", (REPORTS / "null_report.md").is_file(), "null_report.md")
    check("Reporte de atípicos existe", (REPORTS / "outlier_report.md").is_file(), "outlier_report.md")

    def relative(path: Path) -> str:
        return path.relative_to(ROOT).as_posix()

    lines: list[str] = [
        "# Validación del dataset procesado",
        "",
        "Generado automáticamente por `scripts_evidencia/validar_dataset_procesado.py`.",
        "El script solo lee los archivos; ante una discrepancia falla y no corrige datos.",
        "",
        "## Entradas validadas",
        "",
        *[f"- `{relative(path)}`" for path in INPUTS.values()],
        "",
        "## Salidas generadas por el pipeline",
        "",
        *[f"- `{relative(path)}`" for path in GENERATED_OUTPUTS],
        "",
        "## Resultados",
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
