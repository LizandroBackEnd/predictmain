"""Convierte el expediente Markdown a PDF usando Chrome en modo headless.

No hay pandoc en el entorno, por eso el conversor cubre solo el subconjunto
usado por el documento: encabezados, tablas, listas, código, citas y reglas.
El HTML se genera en la misma carpeta y se elimina al terminar.
"""

from __future__ import annotations

import html
import re
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "entrega_sprint2" / "expediente_tecnico_sprint2.md"
DESTINO = SRC.with_suffix(".pdf")
TEMP_HTML = SRC.with_suffix(".render.html")
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")

CSS = """
@page { size: Letter; margin: 17mm 15mm; }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9.6pt; line-height: 1.32; color: #111; }
h1 { font-size: 20pt; margin: 10pt 0 8pt; }
h2 { font-size: 14pt; margin: 16pt 0 6pt; border-bottom: 1px solid #bbb; padding-bottom: 3pt; }
h3 { font-size: 11pt; margin: 11pt 0 4pt; }
p, li { orphans: 2; widows: 2; }
table { border-collapse: collapse; width: 100%; font-size: 7.8pt; margin: 6pt 0; }
th, td { border: 1px solid #999; padding: 3pt 4pt; vertical-align: top; }
th { background: #ececec; }
pre { white-space: pre-wrap; font-size: 7.6pt; background: #f4f4f4; border: 1px solid #ddd;
      padding: 6pt; margin: 6pt 0; }
code { font-family: Consolas, 'Courier New', monospace; }
blockquote { border-left: 3px solid #888; margin: 6pt 0; padding-left: 8pt; color: #444; }
.cover { page-break-after: always; text-align: center; margin-top: 55mm; }
.cover h1 { font-size: 25pt; }
.cover p { font-size: 11pt; margin: 5pt 0; }
.pagebreak { page-break-before: always; }
hr { border: 0; border-top: 1px solid #ccc; margin: 10pt 0; }
"""


def _enlinea(texto: str) -> str:
    partes = texto.split("`")
    escapadas = [
        f"<code>{html.escape(p)}</code>" if i % 2 else html.escape(p)
        for i, p in enumerate(partes)
    ]
    salida = "".join(escapadas)
    salida = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", salida)
    salida = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', salida)
    return salida


def _celdas(fila: str) -> list[str]:
    return [celda.strip() for celda in fila.strip().strip("|").split("|")]


def markdown_a_html(texto: str) -> str:
    lineas = texto.splitlines()
    bloque: list[str] = []
    salida: list[str] = []
    i = 0

    def vaciar() -> None:
        if bloque:
            salida.append(f"<p>{_enlinea(' '.join(bloque))}</p>")
            bloque.clear()

    while i < len(lineas):
        linea = lineas[i]
        if not linea.strip():
            vaciar()
            i += 1
            continue
        if linea.startswith("```"):
            vaciar()
            codigo: list[str] = []
            i += 1
            while i < len(lineas) and not lineas[i].startswith("```"):
                codigo.append(lineas[i])
                i += 1
            salida.append("<pre><code>" + html.escape("\n".join(codigo)) + "</code></pre>")
            i += 1
            continue
        if linea.startswith("|"):
            vaciar()
            tabla: list[str] = []
            while i < len(lineas) and lineas[i].startswith("|"):
                tabla.append(lineas[i])
                i += 1
            cabecera = "".join(f"<th>{_enlinea(c)}</th>" for c in _celdas(tabla[0]))
            filas = []
            for fila in tabla[2:]:
                filas.append("<tr>" + "".join(f"<td>{_enlinea(c)}</td>" for c in _celdas(fila)) + "</tr>")
            salida.append(f"<table><thead><tr>{cabecera}</tr></thead><tbody>{''.join(filas)}</tbody></table>")
            continue
        encabezado = re.match(r"^(#{1,6})\s+(.*)$", linea)
        if encabezado:
            vaciar()
            nivel = len(encabezado.group(1))
            salida.append(f"<h{nivel}>{_enlinea(encabezado.group(2))}</h{nivel}>")
            i += 1
            continue
        if linea.strip() == "---":
            vaciar()
            salida.append("<hr>")
            i += 1
            continue
        if linea.startswith("<!--") or (linea.startswith("<") and linea.endswith(">")):
            vaciar()
            salida.append(linea)
            i += 1
            continue
        if linea.startswith("> "):
            vaciar()
            citas: list[str] = []
            while i < len(lineas) and lineas[i].startswith("> "):
                citas.append(lineas[i][2:])
                i += 1
            salida.append(f"<blockquote>{_enlinea(' '.join(citas))}</blockquote>")
            continue
        if re.match(r"^\s*-\s+", linea):
            vaciar()
            items: list[str] = []
            while i < len(lineas) and re.match(r"^\s*-\s+", lineas[i]):
                items.append(re.sub(r"^\s*-\s+", "", lineas[i]))
                i += 1
            salida.append("<ul>" + "".join(f"<li>{_enlinea(x)}</li>" for x in items) + "</ul>")
            continue
        bloque.append(linea.strip())
        i += 1
    vaciar()
    return f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(salida)}</body></html>"


def main() -> int:
    if not CHROME.is_file():
        raise SystemExit(f"No se encontró Chrome: {CHROME}")
    markdown = SRC.read_text(encoding="utf-8")
    TEMP_HTML.write_text(markdown_a_html(markdown), encoding="utf-8")
    # Perfil único por ejecución: un Chrome previo con el mismo perfil puede
    # capturar la petición y salir sin imprimir nada.
    perfil = Path(tempfile.mkdtemp(prefix="predictmain-pdf-"))
    comando = [
        str(CHROME), "--headless=new", "--disable-gpu", "--no-first-run",
        "--no-default-browser-check", "--allow-file-access-from-files",
        f"--user-data-dir={perfil}", "--no-pdf-header-footer",
        f"--print-to-pdf={DESTINO.as_posix()}", TEMP_HTML.as_uri(),
    ]
    proceso = subprocess.run(comando, check=True, timeout=180, capture_output=True)
    for _ in range(50):
        if DESTINO.is_file() and DESTINO.stat().st_size > 0:
            break
        time.sleep(0.2)
    if not DESTINO.is_file() or DESTINO.stat().st_size == 0:
        raise RuntimeError(f"Chrome no generó el PDF: {proceso.stderr.decode('utf-8', 'replace')}")
    TEMP_HTML.unlink(missing_ok=True)
    print(f"PDF: {DESTINO} ({DESTINO.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
