"""Valida la consistencia de las etiquetas y de los archivos etiquetados.

Las etiquetas fuera del catálogo y las etiquetas contradictorias se reportan por
registro (`UDI`) y hacen fallar la validación; nunca se corrigen ni se convierten.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "03_dataset" / "data" / "raw" / "ai4i2020.csv"
FULL_CSV = ROOT / "04_etiquetado" / "datos" / "datos_etiquetados.csv"
SAMPLE_CSV = ROOT / "04_etiquetado" / "datos" / "muestra_etiquetada.csv"
OUTPUT = ROOT / "04_etiquetado" / "validacion_etiquetado.md"

MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]
TARGET_LABELS = {0: "Sin falla", 1: "Falla"}
NO_MODE_LABEL = "Ninguno"
MAX_LISTED_FINDINGS = 20


def _expected_modes(frame: pd.DataFrame) -> pd.Series:
    active = frame[MODES].astype(int).apply(lambda row: [mode for mode in MODES if row[mode] == 1], axis=1)
    return active.map(lambda modes: ", ".join(modes) if modes else NO_MODE_LABEL)


def _catalog_findings(frame: pd.DataFrame) -> list[tuple[object, str, str]]:
    """Return (UDI, column, value) for every value outside the documented catalog."""
    findings: list[tuple[object, str, str]] = []
    allowed_modes = set(MODES) | {NO_MODE_LABEL}
    for udi, label in frame[["UDI", "etiqueta"]].itertuples(index=False):
        if label not in TARGET_LABELS.values():
            findings.append((udi, "etiqueta", str(label)))
    for udi, value in frame[["UDI", "modos_activos"]].itertuples(index=False):
        tokens = [token.strip() for token in str(value).split(",")]
        invalid = [token for token in tokens if token not in allowed_modes]
        if invalid or (NO_MODE_LABEL in tokens and len(tokens) > 1):
            findings.append((udi, "modos_activos", str(value)))
    return findings


def _conflict_findings(frame: pd.DataFrame) -> list[tuple[object, str, str]]:
    """Return (UDI, column, detail) for labels that contradict their source columns."""
    findings: list[tuple[object, str, str]] = []
    expected_label = frame["Machine failure"].map(TARGET_LABELS)
    for udi, label, expected in zip(frame["UDI"], frame["etiqueta"], expected_label):
        if label in TARGET_LABELS.values() and label != expected:
            findings.append((udi, "etiqueta", f"`{label}` contradice `Machine failure` (esperado `{expected}`)"))
    for udi, value, expected in zip(frame["UDI"], frame["modos_activos"], _expected_modes(frame)):
        if str(value) != expected:
            findings.append((udi, "modos_activos", f"`{value}` contradice las columnas de modo (esperado `{expected}`)"))
    return findings


def _md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> int:
    if not RAW.is_file():
        print(f"No se encontró el dataset original: {RAW}", file=sys.stderr)
        return 1
    df = pd.read_csv(RAW)
    any_mode = df[MODES].sum(axis=1)
    checks: list[tuple[str, bool, str]] = []

    def check(name: str, condition: bool, detail: str) -> None:
        checks.append((name, condition, detail))

    check("Etiqueta objetivo sin valores nulos", int(df["Machine failure"].isna().sum()) == 0, "0 nulos")
    check("Etiqueta objetivo binaria", set(df["Machine failure"].unique()) <= {0, 1}, "valores 0 y 1")
    check("Total de fallas igual a 339", int(df["Machine failure"].sum()) == 339, f"{int(df['Machine failure'].sum())} fallas")
    check("Tipos de producto válidos", set(df["Type"].unique()) <= {"L", "M", "H"}, str(sorted(df["Type"].unique())))
    check(
        "Modos de falla binarios",
        all(set(df[mode].unique()) <= {0, 1} for mode in MODES),
        ", ".join(MODES),
    )
    check("Registros con al menos un modo activo", int((any_mode > 0).sum()) == 348, f"{int((any_mode > 0).sum())} registros")
    check("Registros con múltiples modos activos", int((any_mode > 1).sum()) == 24, f"{int((any_mode > 1).sum())} registros")

    target_zero_mode = df[(df["Machine failure"] == 0) & (any_mode > 0)]
    target_one_no_mode = df[(df["Machine failure"] == 1) & (any_mode == 0)]
    check(
        "Inconsistencias documentadas: objetivo 0 con modo activo",
        len(target_zero_mode) == 18,
        f"{len(target_zero_mode)} registros",
    )
    check(
        "Inconsistencias documentadas: objetivo 1 sin modo activo",
        len(target_one_no_mode) == 9,
        f"{len(target_one_no_mode)} registros",
    )
    check(
        "Total de inconsistencias etiqueta-modo",
        len(target_zero_mode) + len(target_one_no_mode) == 27,
        f"{len(target_zero_mode) + len(target_one_no_mode)} registros",
    )

    findings: list[tuple[str, object, str, str]] = []

    check("Existe el dataset etiquetado completo", FULL_CSV.is_file(), "datos/datos_etiquetados.csv")
    full = pd.read_csv(FULL_CSV) if FULL_CSV.is_file() else None
    if full is not None:
        mapping_ok = full["etiqueta"].eq(full["Machine failure"].map(TARGET_LABELS)).all()
        check("Dataset etiquetado con 10,000 registros", len(full) == 10_000, f"{len(full):,} registros")
        check("Dataset etiquetado conserva 339 fallas", int(full["Machine failure"].sum()) == 339, f"{int(full['Machine failure'].sum())} fallas")
        check("Columna etiqueta sin nulos", int(full["etiqueta"].isna().sum()) == 0, f"{int(full['etiqueta'].isna().sum())} nulos")
        check("Columna modos_activos sin nulos", int(full["modos_activos"].isna().sum()) == 0, f"{int(full['modos_activos'].isna().sum())} nulos")
        check("Etiqueta legible coincide con Machine failure", bool(mapping_ok), "mapeo consistente" if mapping_ok else "mapeo inconsistente")

        catalog = _catalog_findings(full)
        conflicts = _conflict_findings(full)
        findings += [("Fuera del catálogo", udi, column, f"`{value}`") for udi, column, value in catalog]
        findings += [("Etiqueta contradictoria", udi, column, detail) for udi, column, detail in conflicts]
        check("Etiquetas dentro del catálogo", not catalog, f"{len(catalog)} registros fuera del catálogo")
        check("Sin etiquetas contradictorias", not conflicts, f"{len(conflicts)} contradicciones")
        source = df.sort_values("UDI").reset_index(drop=True)
        preserved = (
            len(full) == len(source)
            and all(column in full.columns for column in source.columns)
            and full[list(source.columns)].equals(source)
        )
        check("Columnas originales conservadas sin cambios", preserved, f"{len(source.columns)} columnas comparadas")
    else:
        for name in (
            "Dataset etiquetado con 10,000 registros",
            "Dataset etiquetado conserva 339 fallas",
            "Columna etiqueta sin nulos",
            "Columna modos_activos sin nulos",
            "Etiqueta legible coincide con Machine failure",
            "Etiquetas dentro del catálogo",
            "Sin etiquetas contradictorias",
            "Columnas originales conservadas sin cambios",
        ):
            check(name, False, "archivo no encontrado")

    check("Existe la muestra etiquetada", SAMPLE_CSV.is_file(), "datos/muestra_etiquetada.csv")
    if SAMPLE_CSV.is_file():
        sample = pd.read_csv(SAMPLE_CSV)
        check("Muestra etiquetada con 30 registros", len(sample) == 30, f"{len(sample)} registros")
        check("Muestra etiquetada con 15 fallas", int(sample["Machine failure"].sum()) == 15, f"{int(sample['Machine failure'].sum())} fallas")
        if full is not None:
            merged = sample.merge(full, how="left", on=list(full.columns), indicator=True)
            untraceable = merged.loc[merged["_merge"] != "both", "UDI"].tolist()
            findings += [("Muestra no trazable", udi, "UDI", "el registro no coincide con el dataset completo") for udi in untraceable]
            check("Muestra trazable al dataset completo", not untraceable, f"{len(untraceable)} registros no trazables")
        else:
            check("Muestra trazable al dataset completo", False, "dataset completo no encontrado")
    else:
        check("Muestra etiquetada con 30 registros", False, "archivo no encontrado")
        check("Muestra etiquetada con 15 fallas", False, "archivo no encontrado")
        check("Muestra trazable al dataset completo", False, "archivo no encontrado")

    failures = [name for name, ok, _ in checks if not ok]
    if findings:
        listed = findings[:MAX_LISTED_FINDINGS]
        findings_section = [
            f"Se encontraron {len(findings)} hallazgos que requieren corrección. Se listan los primeros {len(listed)}.",
            "",
            _md_table(["Hallazgo", "UDI", "Columna", "Detalle"], [list(item) for item in listed]),
        ]
    else:
        findings_section = ["Ejecutada: 0 registros fuera del catálogo, 0 etiquetas contradictorias y 0 registros de muestra no trazables."]
    lines = [
        "# Validación del etiquetado",
        "",
        "Generada automáticamente por `scripts/validar_etiquetas.py`.",
        "",
        "## 1. Verificaciones",
        "",
        _md_table(
            ["Verificación", "Resultado", "Detalle"],
            [[name, "OK" if ok else "FALLA", detail] for name, ok, detail in checks],
        ),
        "",
        "## 2. Hallazgos por registro",
        "",
        *findings_section,
        "",
        "## 3. Distribución de etiquetas",
        "",
        _md_table(
            ["Etiqueta", "Registros", "Porcentaje"],
            [
                ["Sin falla (0)", f"{int((df['Machine failure'] == 0).sum()):,}", f"{(df['Machine failure'] == 0).mean() * 100:.2f}%"],
                ["Falla (1)", f"{int((df['Machine failure'] == 1).sum()):,}", f"{(df['Machine failure'] == 1).mean() * 100:.2f}%"],
            ],
        ),
        "",
        "## 4. Distribución de modos de falla",
        "",
        _md_table(["Modo", "Registros"], [[mode, f"{int(df[mode].sum()):,}"] for mode in MODES]),
        "",
        "## 5. Archivos etiquetados",
        "",
        _md_table(
            ["Archivo", "Contenido", "Registros"],
            [
                ["`datos/datos_etiquetados.csv`", "Dataset completo con etiquetas legibles", "10,000"],
                ["`datos/muestra_etiquetada.csv`", "Muestra reproducible para revisión", "30"],
            ],
        ),
        "",
        "## 6. Observaciones",
        "",
        "- La etiqueta `Machine failure` es la variable objetivo oficial del dataset.",
        "- Los modos `TWF`, `HDF`, `PWF`, `OSF` y `RNF` son columnas auxiliares de diagnóstico y pueden solaparse.",
        "- Se identificaron 18 registros con etiqueta 0 pero con algún modo activo; en los 18 el modo activo es `RNF`.",
        "- Se identificaron 9 registros con etiqueta 1 pero sin ningún modo activo.",
        "- Estas 27 inconsistencias se conservan tal como aparecen en el dataset original y se documentan como limitación conocida.",
        "- El dataset etiquetado completo conserva las 14 columnas originales y agrega `etiqueta` y `modos_activos`.",
        "",
    ]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Validación de etiquetado generada en: {OUTPUT}")
    if failures:
        print("Verificaciones fallidas: " + ", ".join(failures))
        return 1
    print(f"Todas las verificaciones de etiquetado pasaron ({len(checks)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
