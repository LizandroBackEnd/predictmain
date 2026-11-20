"""Extrae, limpia y normaliza el texto del corpus PDF de PredictMain.

Requiere: pip install pypdf
"""

from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

from pypdf import PdfReader
from pypdf.errors import PdfReadError

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "corpus_original" / "PredictMain_Corpus_Contenido.pdf"
SALIDAS = ROOT / "salidas"
EVIDENCIAS = ROOT / "evidencias"

PAGE_MARKER = re.compile(r"^=====\s*PAGINA\s+\d+\s*=====$", re.IGNORECASE)
PAGE_NUMBER = re.compile(r"^(p[aá]gina|page)\s+\d+(\s+de\s+\d+)?$", re.IGNORECASE)
ONLY_NUMBER = re.compile(r"^\d{1,3}$")
ONLY_PUNCT = re.compile(r"^[\W_]+$")
SECTION_HEADING = re.compile(r"^\d{1,2}\s*\.\s+[A-ZÁÉÍÓÚÑ]")
TRAILING_HYPHEN = re.compile(r"[a-záéíóúñ]-$")


def extraer_pdf(pdf_path: Path) -> tuple[dict[str, str], list[dict[str, object]]]:
    """Extract metadata and text while preserving the original page order."""
    reader = PdfReader(str(pdf_path))
    metadata = {str(key): str(value) for key, value in (reader.metadata or {}).items()}
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text(extraction_mode="layout") or ""
        pages.append({"pagina": index, "texto": text})
    return metadata, pages


def normalizar_caracteres(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u00a0", " ").replace("\u2007", " ").replace("\u202f", " ")
    text = re.sub(r"[\u200b-\u200d\ufeff]", "", text)
    text = text.replace("\t", " ")
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    text = text.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    text = text.replace("–", "-").replace("—", "-")
    return text


def detectar_lineas_repetidas(pages: list[dict[str, object]], umbral: float = 0.5) -> set[str]:
    contador: Counter[str] = Counter()
    for page in pages:
        lineas = {line.strip().lower() for line in str(page["texto"]).splitlines() if line.strip()}
        contador.update(lineas)

    total = len(pages)
    repetidas = set()
    for linea, frecuencia in contador.items():
        if frecuencia / total >= umbral and len(linea) <= 100:
            if not SECTION_HEADING.match(linea):
                repetidas.add(linea)
    return repetidas


def limpiar_paginas(pages: list[dict[str, object]], repetidas: set[str]) -> tuple[str, dict[str, int]]:
    metricas = {
        "lineas_entrada": 0,
        "lineas_vacias_eliminadas": 0,
        "numeros_pagina_eliminados": 0,
        "encabezados_repetidos_eliminados": 0,
        "lineas_puntuacion_eliminadas": 0,
        "espacios_colapsados": 0,
        "guiones_unidos": 0,
        "caracteres_control_eliminados": 0,
    }
    salida: list[str] = []
    for page in pages:
        texto = normalizar_caracteres(str(page["texto"]))
        lineas = texto.splitlines()
        lineas_limpias: list[str] = []
        separador_pendiente = False
        for linea in lineas:
            metricas["lineas_entrada"] += 1
            if not linea.strip():
                metricas["lineas_vacias_eliminadas"] += 1
                separador_pendiente = True
                continue
            if PAGE_MARKER.match(linea.strip()):
                continue
            if PAGE_NUMBER.match(linea.strip()) or ONLY_NUMBER.match(linea.strip()):
                metricas["numeros_pagina_eliminados"] += 1
                continue
            if linea.strip().lower() in repetidas:
                metricas["encabezados_repetidos_eliminados"] += 1
                continue
            if ONLY_PUNCT.match(linea.strip()):
                metricas["lineas_puntuacion_eliminadas"] += 1
                continue
            colapsada = re.sub(r"[ ]{2,}", " ", linea).strip()
            if colapsada != linea.strip():
                metricas["espacios_colapsados"] += 1
            if separador_pendiente and lineas_limpias:
                lineas_limpias.append("")
            separador_pendiente = False
            lineas_limpias.append(colapsada)

        for linea in lineas_limpias:
            if not linea:
                if salida and salida[-1] != "":
                    salida.append("")
                continue
            if salida and TRAILING_HYPHEN.search(salida[-1]) and linea[:1].islower():
                salida[-1] = salida[-1][:-1] + linea
                metricas["guiones_unidos"] += 1
            else:
                salida.append(linea)
        if salida and salida[-1] != "":
            salida.append("")

    texto_limpio = "\n".join(salida)
    texto_limpio = re.sub(r"\n{3,}", "\n\n", texto_limpio).strip() + "\n"
    return texto_limpio, metricas


def main() -> int:
    if not PDF.is_file():
        raise FileNotFoundError(f"No se encontró el corpus: {PDF}")
    if PDF.stat().st_size == 0:
        raise ValueError(f"El corpus original está vacío: {PDF}")

    SALIDAS.mkdir(parents=True, exist_ok=True)
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)

    try:
        metadata, pages = extraer_pdf(PDF)
    except PdfReadError as error:
        raise ValueError(f"No se pudo leer el corpus PDF {PDF}: {error}") from error
    if not pages or any(not str(page["texto"]).strip() for page in pages):
        raise ValueError("La extracción produjo páginas vacías; se cancela la salida.")
    repetidas = detectar_lineas_repetidas(pages)
    texto_limpio, metricas = limpiar_paginas(pages, repetidas)
    texto_extraido = "\n\n".join(
        f"===== PAGINA {page['pagina']} =====\n{page['texto']}" for page in pages
    )

    (SALIDAS / "corpus_extraido.txt").write_text(texto_extraido, encoding="utf-8")
    (SALIDAS / "corpus_extraido.json").write_text(
        json.dumps({"metadata": metadata, "paginas": pages}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (SALIDAS / "corpus_limpio.txt").write_text(texto_limpio, encoding="utf-8")
    if not texto_limpio.strip():
        raise ValueError("La limpieza produjo un corpus vacío; se cancela la evidencia.")

    caracteres_extraidos = len(texto_extraido)
    caracteres_limpios = len(texto_limpio)
    reporte = [
        "# Reporte de limpieza y normalización del corpus",
        "",
        f"- Archivo fuente: `{PDF.name}`",
        f"- Páginas: {len(pages)}",
        f"- Caracteres extraídos: {caracteres_extraidos:,}",
        f"- Caracteres después de limpieza: {caracteres_limpios:,}",
        f"- Porcentaje conservado: {caracteres_limpios / caracteres_extraidos * 100:.2f}%",
        f"- Líneas de entrada: {metricas['lineas_entrada']:,}",
        f"- Líneas vacías eliminadas: {metricas['lineas_vacias_eliminadas']:,}",
        f"- Números de página eliminados: {metricas['numeros_pagina_eliminados']:,}",
        f"- Encabezados repetidos eliminados: {metricas['encabezados_repetidos_eliminados']:,}",
        f"- Líneas de solo puntuación eliminadas: {metricas['lineas_puntuacion_eliminadas']:,}",
        f"- Líneas con espacios colapsados: {metricas['espacios_colapsados']:,}",
        f"- Guiones de corte unidos: {metricas['guiones_unidos']:,}",
        "",
        "## Archivos generados",
        "",
        "- `salidas/corpus_extraido.txt`: texto extraído con marcadores de página.",
        "- `salidas/corpus_extraido.json`: metadatos y texto por página.",
        "- `salidas/corpus_limpio.txt`: texto normalizado antes de la deduplicación.",
        "",
    ]
    (EVIDENCIAS / "reporte_limpieza_corpus.md").write_text("\n".join(reporte), encoding="utf-8")

    print(f"Páginas extraídas: {len(pages)}")
    print(f"Caracteres extraídos: {caracteres_extraidos:,}")
    print(f"Caracteres limpios: {caracteres_limpios:,}")
    print(f"Reporte: {EVIDENCIAS / 'reporte_limpieza_corpus.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
