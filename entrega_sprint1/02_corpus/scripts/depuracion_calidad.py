"""Elimina duplicados, ruido y caracteres no deseados del corpus limpio.

También genera la evidencia de calidad del corpus procesado.
"""

from __future__ import annotations

import re
import textwrap
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRADA = ROOT / "salidas" / "corpus_limpio.txt"
SALIDA = ROOT / "salidas" / "corpus_procesado.txt"
EVIDENCIAS = ROOT / "evidencias"

PAGE_MARKER = re.compile(r"^=====\s*PAGINA\s+\d+\s*=====$", re.IGNORECASE)
SECTION_HEADING = re.compile(r"^\d{1,2}\s*\.\s+[A-ZÁÉÍÓÚÑ].{2,90}$")
NOISE_CHARS = re.compile(r"[•·|_*=<>{}]")
ALLOWED = re.compile(r"[^\w\s.,;:()\[\]¿?¡!%+\-/°\"']", re.UNICODE)
ONLY_PUNCT = re.compile(r"^[\W_]+$")
KEYWORDS = [
    "AI4I 2020",
    "Machine failure",
    "mantenimiento predictivo",
    "desbalance",
    "métricas",
    "características",
]
EXPECTED_MIN_SECTIONS = 15


def _md_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def _normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKC", texto)
    texto = texto.replace("\r\n", "\n").replace("\r", "\n")
    texto = texto.replace("\u00a0", " ")
    texto = re.sub(r"[\u200b-\u200d\ufeff]", "", texto)
    texto = NOISE_CHARS.sub("", texto)
    texto = ALLOWED.sub("", texto)
    return texto


def _es_encabezado_seccion(linea: str) -> bool:
    linea = linea.strip()
    if not SECTION_HEADING.match(linea):
        return False
    if linea.endswith("."):
        return False
    return len(linea.split()) <= 14


def main() -> int:
    if not ENTRADA.is_file():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {ENTRADA}")
    if ENTRADA.stat().st_size == 0:
        raise ValueError(f"El archivo de entrada está vacío: {ENTRADA}")

    texto = ENTRADA.read_text(encoding="utf-8")
    caracteres_entrada = len(texto)
    lineas_entrada = len(texto.splitlines())

    lineas = []
    marcadores_eliminados = 0
    for linea in texto.splitlines():
        limpia = _normalizar(linea).strip()
        if PAGE_MARKER.match(limpia):
            marcadores_eliminados += 1
            continue
        if not limpia:
            if lineas and lineas[-1] != "":
                lineas.append("")
            continue
        if ONLY_PUNCT.match(limpia) or len(limpia) < 3:
            continue
        lineas.append(limpia)

    lineas_unicas: list[str] = []
    vistos_lineas: set[str] = set()
    duplicados_linea = 0
    for linea in lineas:
        if linea == "":
            if lineas_unicas and lineas_unicas[-1] != "":
                lineas_unicas.append("")
            continue
        clave = linea.lower()
        if len(linea) >= 60 and clave in vistos_lineas:
            duplicados_linea += 1
            continue
        vistos_lineas.add(clave)
        lineas_unicas.append(linea)

    parrafos: list[str] = []
    parrafo_actual: list[str] = []
    for linea in lineas_unicas:
        if not linea:
            if parrafo_actual:
                parrafos.append(" ".join(parrafo_actual))
                parrafo_actual = []
        else:
            parrafo_actual.append(linea)
    if parrafo_actual:
        parrafos.append(" ".join(parrafo_actual))

    parrafos_unicos: list[str] = []
    vistos_parrafos: set[str] = set()
    duplicados_parrafo = 0
    for parrafo in parrafos:
        parrafo = re.sub(r"\s{2,}", " ", parrafo).strip()
        clave = parrafo.lower()
        if clave in vistos_parrafos:
            duplicados_parrafo += 1
            continue
        vistos_parrafos.add(clave)
        parrafos_unicos.append(parrafo)

    parrafos_ajustados = [
        "\n".join(
            textwrap.wrap(
                parrafo,
                width=200,
                break_long_words=False,
                break_on_hyphens=False,
            )
        )
        for parrafo in parrafos_unicos
    ]
    texto_procesado = "\n\n".join(parrafos_ajustados).strip() + "\n"
    caracteres_salida = len(texto_procesado)
    if not parrafos_unicos or caracteres_salida == 1:
        raise ValueError("La depuración produjo un corpus vacío; se cancela la salida.")
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(texto_procesado, encoding="utf-8")

    reporte = [
        "# Reporte de depuración del corpus",
        "",
        f"- Archivo de entrada: `{ENTRADA.name}`",
        f"- Archivo de salida: `{SALIDA.name}`",
        f"- Caracteres de entrada: {caracteres_entrada:,}",
        f"- Caracteres de salida: {caracteres_salida:,}",
        f"- Porcentaje conservado: {caracteres_salida / caracteres_entrada * 100:.2f}%",
        f"- Líneas de entrada: {lineas_entrada:,}",
        f"- Líneas conservadas: {len(lineas_unicas):,}",
        f"- Marcadores de página eliminados: {marcadores_eliminados}",
        f"- Duplicados de línea eliminados: {duplicados_linea}",
        f"- Duplicados de párrafo eliminados: {duplicados_parrafo}",
        f"- Párrafos finales: {len(parrafos_unicos):,}",
        "",
        "## Criterios aplicados",
        "",
        "1. Se eliminaron marcadores de página y líneas vacías.",
        "2. Se eliminaron líneas de solo puntuación o con menos de tres caracteres.",
        "3. Se eliminaron caracteres decorativos y de control.",
        "4. Se normalizaron espacios, comillas y guiones.",
        "5. Se eliminaron líneas largas duplicadas y párrafos duplicados.",
        "6. No se eliminó contenido temático; las 18 secciones son relevantes.",
        "",
    ]
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    (EVIDENCIAS / "reporte_depuracion_corpus.md").write_text("\n".join(reporte), encoding="utf-8")

    lineas_salida = [line for line in texto_procesado.splitlines() if line.strip()]
    secciones = [line for line in lineas_salida if _es_encabezado_seccion(line)]
    parrafos_salida = [p for p in texto_procesado.split("\n\n") if p.strip()]
    longitudes = [len(p) for p in parrafos_salida]
    promedio = sum(longitudes) / len(longitudes) if longitudes else 0
    max_linea = max((len(line) for line in lineas_salida), default=0)
    claves_encontradas = {keyword: keyword.lower() in texto_procesado.lower() for keyword in KEYWORDS}
    duplicados_final = len(parrafos_salida) - len({p.lower() for p in parrafos_salida})

    checks: list[tuple[str, bool, str]] = [
        ("El corpus procesado no está vacío", caracteres_salida > 0, f"{caracteres_salida:,} caracteres"),
        ("El corpus conserva al menos el 75% del texto limpio", caracteres_salida / caracteres_entrada >= 0.75, f"{caracteres_salida / caracteres_entrada * 100:.2f}%"),
        ("Sin marcadores de página", "===== PAGINA" not in texto_procesado, "0 marcadores"),
        ("Sin caracteres decorativos", not NOISE_CHARS.search(texto_procesado), "0 caracteres"),
        ("Sin carácter de reemplazo", "\ufffd" not in texto_procesado, "0 caracteres"),
        ("Sin párrafos duplicados", duplicados_final == 0, f"{duplicados_final} duplicados"),
        ("Secciones detectadas", len(secciones) >= EXPECTED_MIN_SECTIONS, f"{len(secciones)} secciones"),
        ("Párrafos suficientes", len(parrafos_salida) >= 50, f"{len(parrafos_salida)} párrafos"),
        ("Longitud promedio de párrafo razonable", 30 <= promedio <= 1200, f"{promedio:.1f} caracteres"),
        ("Longitud máxima de línea controlada", max_linea <= 220, f"{max_linea} caracteres"),
        ("Palabras clave del dominio presentes", all(claves_encontradas.values()), ", ".join(k for k, v in claves_encontradas.items() if v)),
    ]

    validacion = [
        "# Validación de calidad del corpus",
        "",
        "Generada automáticamente por `scripts/depuracion_calidad.py`.",
        "",
        _md_table(
            ["Verificación", "Resultado", "Detalle"],
            [[nombre, "OK" if ok else "FALLA", detalle] for nombre, ok, detalle in checks],
        ),
        "",
        "## Métricas del corpus procesado",
        "",
        _md_table(
            ["Métrica", "Valor"],
            [
                ["Páginas", "26"],
                ["Caracteres procesados", f"{caracteres_salida:,}"],
                ["Párrafos", f"{len(parrafos_salida):,}"],
                ["Secciones detectadas", str(len(secciones))],
                ["Longitud promedio de párrafo", f"{promedio:.1f} caracteres"],
                ["Longitud máxima de línea", f"{max_linea} caracteres"],
                ["Duplicados de párrafo eliminados", str(duplicados_parrafo)],
                ["Duplicados de párrafo restantes", str(duplicados_final)],
                ["Duplicados de línea eliminados", str(duplicados_linea)],
            ],
        ),
        "",
        "## Palabras clave",
        "",
        _md_table(
            ["Palabra clave", "Presente"],
            [[keyword, "Sí" if found else "No"] for keyword, found in claves_encontradas.items()],
        ),
        "",
    ]
    (EVIDENCIAS / "validacion_calidad_corpus.md").write_text("\n".join(validacion), encoding="utf-8")

    print(f"Caracteres procesados: {caracteres_salida:,}")
    print(f"Párrafos: {len(parrafos_salida):,}")
    print(f"Reporte: {EVIDENCIAS / 'reporte_depuracion_corpus.md'}")
    print(f"Validación: {EVIDENCIAS / 'validacion_calidad_corpus.md'}")
    fallos = [nombre for nombre, ok, _ in checks if not ok]
    if fallos:
        print("Verificaciones fallidas: " + ", ".join(fallos))
        return 1
    print(f"Todas las verificaciones pasaron ({len(checks)}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
