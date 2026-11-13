"""Reconcilia la copia de entrega de Sprint 1 con las fuentes canónicas del proyecto.

Compara el manifiesto, el dataset crudo, los datasets procesados, el código del
pipeline, las dependencias y el artefacto serializado. Es de solo lectura: nunca
modifica las fuentes canónicas ni la copia de entrega; solo escribe la evidencia.

Uso, desde la raíz del repositorio:
    python entrega_sprint1/03_dataset/scripts_evidencia/reconciliar_entrega.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANONICAL_ROOT = ROOT.parents[1]
OUTPUT = ROOT / "evidencias" / "reconciliacion_entrega.md"

EXPECTED_ROWS = 10000
EXPECTED_COLUMNS = 14
MANIFEST_FIELDS = ["file_name", "sha256", "n_rows", "n_columns", "columns", "size_bytes"]
DATA_FILES = [
    "raw/ai4i2020.csv",
    "processed/ai4i2020_clean.csv",
    "processed/ai4i2020_outlier_analyzed.csv",
    "processed/ai4i2020_transformed.csv",
]
ML_FILES = ["requirements.txt", "artifacts/pipeline.joblib"]


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


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"No se encontró el archivo requerido: {path}")
    if path.stat().st_size == 0:
        raise ValueError(f"El archivo requerido está vacío: {path}")


def _source_files(ml_root: Path) -> list[str]:
    return sorted(
        path.relative_to(ml_root).as_posix()
        for path in (ml_root / "src").rglob("*.py")
        if "__pycache__" not in path.parts
    )


def _load_pipeline(ml_root: Path) -> str:
    """Load the delivery artifact with the delivery sources on the import path."""
    import joblib

    sys.path.insert(0, str(ml_root))
    try:
        pipeline = joblib.load(ml_root / "artifacts" / "pipeline.joblib")
    finally:
        sys.path.remove(str(ml_root))
    return type(pipeline).__name__


def reconcile(canonical_root: Path) -> list[tuple[str, bool, str]]:
    delivery_data = ROOT / "data"
    delivery_ml = ROOT / "ml_service"
    canonical_data = canonical_root / "data"
    canonical_ml = canonical_root / "ml_service"

    canonical_manifest_path = canonical_data / "raw" / "manifest.json"
    delivery_manifest_path = delivery_data / "raw" / "manifest.json"
    for path in (
        canonical_data / "raw" / "ai4i2020.csv",
        delivery_data / "raw" / "ai4i2020.csv",
        canonical_manifest_path,
        delivery_manifest_path,
    ):
        _require_file(path)

    results: list[tuple[str, bool, str]] = []

    canonical_manifest = json.loads(canonical_manifest_path.read_text(encoding="utf-8"))
    delivery_manifest = json.loads(delivery_manifest_path.read_text(encoding="utf-8"))
    for field in MANIFEST_FIELDS:
        expected, actual = canonical_manifest.get(field), delivery_manifest.get(field)
        detail = "coincide" if expected == actual else f"canónico={expected!r}; entrega={actual!r}"
        results.append((f"Manifiesto: campo `{field}`", expected == actual, detail))

    canonical_hash = _sha256(canonical_data / "raw" / "ai4i2020.csv")
    results.append((
        "Manifiesto canónico describe el CSV canónico",
        canonical_manifest.get("sha256") == canonical_hash,
        canonical_hash,
    ))
    raw = pd.read_csv(delivery_data / "raw" / "ai4i2020.csv")
    results.append((
        "CSV crudo de entrega con 10.000 filas y 14 columnas",
        raw.shape == (EXPECTED_ROWS, EXPECTED_COLUMNS),
        str(raw.shape),
    ))

    for relative in DATA_FILES:
        canonical, delivery = canonical_data / relative, delivery_data / relative
        if not delivery.is_file() or not canonical.is_file():
            missing = delivery if not delivery.is_file() else canonical
            results.append((f"Copia `data/{relative}`", False, f"falta {missing}"))
            continue
        same = _sha256(canonical) == _sha256(delivery)
        detail = "SHA-256 idéntico" if same else f"copia desactualizada: {delivery}"
        results.append((f"Copia `data/{relative}`", same, detail))

    canonical_sources = set(_source_files(canonical_ml))
    delivery_sources = set(_source_files(delivery_ml))
    for relative in sorted(canonical_sources | delivery_sources) + ML_FILES:
        canonical, delivery = canonical_ml / relative, delivery_ml / relative
        if not delivery.is_file():
            results.append((f"Copia `ml_service/{relative}`", False, f"falta en la entrega: {delivery}"))
            continue
        if not canonical.is_file():
            results.append((f"Copia `ml_service/{relative}`", False, f"no existe en la fuente canónica: {canonical}"))
            continue
        same = _sha256(canonical) == _sha256(delivery)
        detail = "SHA-256 idéntico" if same else f"copia desactualizada: {delivery}"
        results.append((f"Copia `ml_service/{relative}`", same, detail))

    try:
        loaded = _load_pipeline(delivery_ml)
        results.append(("Artefacto `pipeline.joblib` cargable", True, loaded))
    except Exception as error:  # noqa: BLE001 - any load failure is a reconciliation failure
        results.append(("Artefacto `pipeline.joblib` cargable", False, f"{type(error).__name__}: {error}"))

    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--canonical-root",
        type=Path,
        default=DEFAULT_CANONICAL_ROOT,
        help="Raíz del proyecto que contiene `data/` y `ml_service/` canónicos.",
    )
    args = parser.parse_args(argv)

    try:
        results = reconcile(args.canonical_root.resolve())
    except (FileNotFoundError, ValueError) as error:
        print(f"Error de reconciliación: {error}", file=sys.stderr)
        return 1

    lines = [
        "# Reconciliación de la entrega con las fuentes canónicas",
        "",
        "Generado automáticamente por `scripts_evidencia/reconciliar_entrega.py`.",
        "",
        "- Fuente canónica: `data/` y `ml_service/` en la raíz del repositorio (solo lectura).",
        "- Copia de entrega: `entrega_sprint1/03_dataset/data/` y `entrega_sprint1/03_dataset/ml_service/`.",
        "",
        _md_table(
            ["Verificación", "Resultado", "Detalle"],
            [[name, "OK" if ok else "FALLA", detail] for name, ok, detail in results],
        ),
        "",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Reconciliación generada en: {OUTPUT}")

    failures = [(name, detail) for name, ok, detail in results if not ok]
    if failures:
        print("Verificaciones fallidas:")
        for name, detail in failures:
            print(f"- {name}: {detail}")
        return 1
    print(f"Todas las verificaciones pasaron ({len(results)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
