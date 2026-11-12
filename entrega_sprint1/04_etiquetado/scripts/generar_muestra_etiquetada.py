"""Genera el dataset etiquetado completo y una muestra reproducible."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "03_dataset" / "data" / "raw" / "ai4i2020.csv"
OUT_DIR = ROOT / "04_etiquetado" / "datos"
FULL_CSV = OUT_DIR / "datos_etiquetados.csv"
SAMPLE_CSV = OUT_DIR / "muestra_etiquetada.csv"
SAMPLE_MD = ROOT / "04_etiquetado" / "muestra_etiquetada.md"

MODES = ["TWF", "HDF", "PWF", "OSF", "RNF"]
SENSOR_COLUMNS = [
    "Air temperature [K]",
    "Process temperature [K]",
    "Rotational speed [rpm]",
    "Torque [Nm]",
    "Tool wear [min]",
]


def _modes_label(row: pd.Series) -> str:
    active = [mode for mode in MODES if int(row[mode]) == 1]
    return ", ".join(active) if active else "Ninguno"


def _md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def main() -> int:
    df = pd.read_csv(RAW)
    df["etiqueta"] = df["Machine failure"].map({0: "Sin falla", 1: "Falla"})
    df["modos_activos"] = df.apply(_modes_label, axis=1)

    ordered_columns = [
        "UDI",
        "Product ID",
        "Type",
        *SENSOR_COLUMNS,
        "Machine failure",
        *MODES,
        "etiqueta",
        "modos_activos",
    ]
    full = df[ordered_columns].sort_values("UDI").reset_index(drop=True)

    samples = []
    for (target, product_type), group in df.groupby(["Machine failure", "Type"]):
        take = min(5, len(group))
        samples.append(group.sample(n=take, random_state=42))
    sample = pd.concat(samples).sort_values(["Machine failure", "Type", "UDI"]).reset_index(drop=True)
    sample = sample[ordered_columns]

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full.to_csv(FULL_CSV, index=False, encoding="utf-8")
    sample.to_csv(SAMPLE_CSV, index=False, encoding="utf-8")

    any_mode = full[MODES].sum(axis=1)
    target_zero_mode = full[(full["Machine failure"] == 0) & (any_mode > 0)]
    target_one_no_mode = full[(full["Machine failure"] == 1) & (any_mode == 0)]

    display_columns = ["UDI", "Type", *SENSOR_COLUMNS, "Machine failure", "etiqueta", "modos_activos"]
    lines = [
        "# Muestra etiquetada del dataset AI4I 2020",
        "",
        "Generada automáticamente por `scripts/generar_muestra_etiquetada.py` con `random_state=42`.",
        "",
        "## 1. Archivos generados",
        "",
        _md_table(
            ["Archivo", "Contenido", "Registros"],
            [
                ["`datos/datos_etiquetados.csv`", "Dataset completo con etiquetas legibles", f"{len(full):,}"],
                ["`datos/muestra_etiquetada.csv`", "Muestra reproducible para revisión humana", f"{len(sample)}"],
            ],
        ),
        "",
        "## 2. Dataset etiquetado completo",
        "",
        _md_table(
            ["Métrica", "Valor"],
            [
                ["Registros", f"{len(full):,}"],
                ["Fallas", f"{int(full['Machine failure'].sum()):,}"],
                ["Sin falla", f"{int((full['Machine failure'] == 0).sum()):,}"],
                ["Registros con al menos un modo activo", f"{int((any_mode > 0).sum()):,}"],
                ["Registros con múltiples modos", f"{int((any_mode > 1).sum()):,}"],
                ["Etiqueta 0 con modo activo", f"{len(target_zero_mode):,}"],
                ["Etiqueta 1 sin modo activo", f"{len(target_one_no_mode):,}"],
            ],
        ),
        "",
        "## 3. Esquema del dataset etiquetado",
        "",
        _md_table(
            ["Columna", "Descripción"],
            [
                ["`UDI`", "Identificador único del registro."],
                ["`Product ID`", "Identificador del producto."],
                ["`Type`", "Tipo de producto: L, M o H."],
                ["Variables de sensores", "Temperaturas, RPM, torque y desgaste."],
                ["`Machine failure`", "Etiqueta original 0/1."],
                ["`TWF`, `HDF`, `PWF`, `OSF`, `RNF`", "Modos de falla binarios."],
                ["`etiqueta`", "Etiqueta legible: `Sin falla` o `Falla`."],
                ["`modos_activos`", "Lista de modos activos o `Ninguno`."],
            ],
        ),
        "",
        "## 4. Muestra para revisión humana",
        "",
        f"- Registros de la muestra: **{len(sample)}**",
        f"- Fallas en la muestra: **{int(sample['Machine failure'].sum())}**",
        f"- Sin falla en la muestra: **{int((sample['Machine failure'] == 0).sum())}**",
        "",
        _md_table(display_columns, sample[display_columns].values.tolist()),
        "",
        "## 5. Diccionario de etiquetas",
        "",
        _md_table(
            ["Etiqueta", "Significado"],
            [
                ["Sin falla", "`Machine failure = 0`; el registro no representa una falla operativa."],
                ["Falla", "`Machine failure = 1`; el registro representa una falla operativa."],
                ["Ninguno", "No se activó ningún modo de falla específico."],
                ["TWF", "Tool Wear Failure: falla por desgaste de herramienta."],
                ["HDF", "Heat Dissipation Failure: falla por disipación de calor."],
                ["PWF", "Power Failure: falla por potencia."],
                ["OSF", "Overstrain Failure: falla por sobreesfuerzo."],
                ["RNF", "Random Failure: falla aleatoria."],
            ],
        ),
        "",
        "## 6. Reproducibilidad",
        "",
        "```powershell",
        "python scripts/generar_muestra_etiquetada.py",
        "```",
        "",
        "La muestra no se usa para entrenar; su propósito es facilitar la revisión y validación de etiquetas.",
        "",
    ]
    SAMPLE_MD.write_text("\n".join(lines), encoding="utf-8")

    print(f"Dataset etiquetado generado en: {FULL_CSV}")
    print(f"Muestra CSV generada en: {SAMPLE_CSV}")
    print(f"Documento de muestra generado en: {SAMPLE_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
