"""Valida la consistencia de las etiquetas y de los archivos etiquetados."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "03_dataset" / "data" / "raw" / "ai4i2020.csv"
FULL_CSV = ROOT / "04_etiquetado" / "datos" / "datos_etiquetados.csv"
SAMPLE_CSV = ROOT / "04_etiquetado" / "datos" / "muestra_etiquetada.csv"
OUTPUT = ROOT / "04_etiquetado" / "validacion_etiquetado.md"

MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]


def _md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> int:
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

    check("Existe el dataset etiquetado completo", FULL_CSV.is_file(), "datos/datos_etiquetados.csv")
    if FULL_CSV.is_file():
        full = pd.read_csv(FULL_CSV)
        mapping_ok = (
            full["etiqueta"].eq(full["Machine failure"].map({0: "Sin falla", 1: "Falla"})).all()
        )
        check("Dataset etiquetado con 10,000 registros", len(full) == 10_000, f"{len(full):,} registros")
        check("Dataset etiquetado conserva 339 fallas", int(full["Machine failure"].sum()) == 339, f"{int(full['Machine failure'].sum())} fallas")
        check("Columna etiqueta sin nulos", int(full["etiqueta"].isna().sum()) == 0, "0 nulos")
        check("Columna modos_activos sin nulos", int(full["modos_activos"].isna().sum()) == 0, "0 nulos")
        check("Etiqueta legible coincide con Machine failure", bool(mapping_ok), "mapeo consistente")
    else:
        check("Dataset etiquetado con 10,000 registros", False, "archivo no encontrado")
        check("Dataset etiquetado conserva 339 fallas", False, "archivo no encontrado")
        check("Columna etiqueta sin nulos", False, "archivo no encontrado")
        check("Columna modos_activos sin nulos", False, "archivo no encontrado")
        check("Etiqueta legible coincide con Machine failure", False, "archivo no encontrado")

    check("Existe la muestra etiquetada", SAMPLE_CSV.is_file(), "datos/muestra_etiquetada.csv")
    if SAMPLE_CSV.is_file():
        sample = pd.read_csv(SAMPLE_CSV)
        check("Muestra etiquetada con 30 registros", len(sample) == 30, f"{len(sample)} registros")
        check("Muestra etiquetada con 15 fallas", int(sample["Machine failure"].sum()) == 15, f"{int(sample['Machine failure'].sum())} fallas")
    else:
        check("Muestra etiquetada con 30 registros", False, "archivo no encontrado")
        check("Muestra etiquetada con 15 fallas", False, "archivo no encontrado")

    failures = [name for name, ok, _ in checks if not ok]
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
        "## 2. Distribución de etiquetas",
        "",
        _md_table(
            ["Etiqueta", "Registros", "Porcentaje"],
            [
                ["Sin falla (0)", f"{int((df['Machine failure'] == 0).sum()):,}", f"{(df['Machine failure'] == 0).mean() * 100:.2f}%"],
                ["Falla (1)", f"{int((df['Machine failure'] == 1).sum()):,}", f"{(df['Machine failure'] == 1).mean() * 100:.2f}%"],
            ],
        ),
        "",
        "## 3. Distribución de modos de falla",
        "",
        _md_table(["Modo", "Registros"], [[mode, f"{int(df[mode].sum()):,}"] for mode in MODES]),
        "",
        "## 4. Archivos etiquetados",
        "",
        _md_table(
            ["Archivo", "Contenido", "Registros"],
            [
                ["`datos/datos_etiquetados.csv`", "Dataset completo con etiquetas legibles", "10,000"],
                ["`datos/muestra_etiquetada.csv`", "Muestra reproducible para revisión", "30"],
            ],
        ),
        "",
        "## 5. Observaciones",
        "",
        "- La etiqueta `Machine failure` es la variable objetivo oficial del dataset.",
        "- Los modos `TWF`, `HDF`, `PWF`, `OSF` y `RNF` son columnas auxiliares de diagnóstico y pueden solaparse.",
        "- Se identificaron 18 registros con etiqueta 0 pero con algún modo activo.",
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
