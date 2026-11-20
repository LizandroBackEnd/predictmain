# Verificación final de la entrega de Sprint 1

Registro de las verificaciones ejecutadas al cerrar la reconciliación de la
entrega. Fecha de ejecución: 2026-11-13 (UTC).

## 1. Entorno

| Elemento | Valor |
|---|---|
| Python | 3.14.4 en un entorno virtual temporal, fuera del repositorio |
| Dependencias | `02_corpus/requirements.txt` (`pypdf==7.0.1`) y `03_dataset/ml_service/requirements.txt` (pandas 3.1.1, scikit-learn 1.9.1) |
| Directorio de trabajo | Raíz del repositorio; el pipeline se ejecutó en una copia temporal limpia de `03_dataset/` |

## 2. Integridad de las fuentes inmutables

| Archivo | SHA-256 esperado | SHA-256 observado | Resultado |
|---|---|---|---|
| `data/raw/ai4i2020.csv` | `59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183` | Igual | OK |
| `entrega_sprint1/03_dataset/data/raw/ai4i2020.csv` | `59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183` | Igual | OK |
| `entrega_sprint1/02_corpus/corpus_original/PredictMain_Corpus_Contenido.pdf` | `78190c534b822d0245a4e98ff51fc6a77af4d52b7c1c295f105b9b0575b04efe` | Igual | OK |

`data/`, `ml_service/` y el PDF original no tienen cambios respecto del último
commit. Los CSV derivados conservan 10,000 filas; el crudo y los procesados
intermedios, 14 columnas, y el transformado, 9.

## 3. Ejecuciones de los paquetes

| Paquete | Comando | Resultado | Evidencia |
|---|---|---|---|
| Corpus | `02_corpus/scripts/limpieza_normalizacion.py` y `02_corpus/scripts/depuracion_calidad.py` | OK, 11 de 11 verificaciones | `02_corpus/evidencias/ejecucion_corpus.log` |
| Pipeline del dataset | Cinco etapas de `python -m src.cli` con rutas explícitas | OK, código 0 en todas; salidas idénticas byte a byte a la entrega | `03_dataset/evidencias/pipeline_ejecucion.log` |
| Reconciliación | `03_dataset/scripts_evidencia/reconciliar_entrega.py` | OK, 36 de 36 | `03_dataset/evidencias/reconciliacion_entrega.md` |
| Comparativa | `03_dataset/scripts_evidencia/comparar_datasets.py` | OK; dos ejecuciones producen el mismo archivo | `03_dataset/evidencias/comparativa_datasets.md` |
| Validación del dataset | `03_dataset/scripts_evidencia/validar_dataset_procesado.py` | OK, 36 de 36 | `03_dataset/evidencias/validacion_dataset.md` |
| Etiquetado | `04_etiquetado/scripts/generar_muestra_etiquetada.py` y `04_etiquetado/scripts/validar_etiquetas.py` | OK, 23 de 23; la muestra es idéntica entre ejecuciones | `04_etiquetado/evidencias/validacion_etiquetado.log` |

## 4. Escenarios de falla verificados

Los escenarios se ejecutaron sobre copias temporales, nunca sobre la entrega ni
sobre las fuentes canónicas.

| Escenario | Comportamiento observado | Resultado |
|---|---|---|
| PDF del corpus inexistente | `FileNotFoundError` con la ruta; código 1 | OK |
| PDF del corpus ilegible | `ValueError` con la ruta y la causa; código 1; salidas sin modificar | OK |
| Corpus procesado con defectos (corpus truncado) | Tres verificaciones en `FALLA`; código 1 | OK |
| Manifiesto de entrega alterado | Falla e identifica el campo (`n_rows`: canónico 10000, entrega 9999) | OK |
| CSV crudo de entrega inexistente | Falla indicando la ruta faltante | OK |
| Código fuente de entrega desactualizado | Falla e indica la ruta desactualizada | OK |
| Artefacto `pipeline.joblib` corrupto | Falla por copia desactualizada y por artefacto no cargable | OK |
| Entrada procesada inexistente | Validación y comparativa fallan con la ruta y no generan reporte | OK |
| Fila eliminada o categoría `Type` inválida | Fallan las verificaciones de filas, distribución y categorías; el archivo no se corrige | OK |
| Etiqueta fuera del catálogo o contradictoria | Falla e identifica `UDI`, columna y valor; el valor no se convierte | OK |
| Registro de muestra alterado | Falla la trazabilidad e identifica el `UDI` | OK |

## 5. Documentación Markdown

| Verificación | Resultado |
|---|---|
| La visión contiene problema, objetivos, alcance, usuarios, arquitectura, datos, criterios de éxito y trazabilidad | OK |
| Los documentos técnicos de corpus, dataset, etiquetado y entrenamiento contienen sus secciones requeridas | OK |
| Todas las rutas citadas entre comillas invertidas existen | OK |
| No se generaron archivos PDF; el único PDF es el corpus original | OK |

## 6. Aplicación web

| Comando | Resultado |
|---|---|
| `bun run lint` | OK, 0 errores; 3 avisos en un archivo de terceros dentro de `ml_service/.venv` |
| `bunx tsc --noEmit` | OK |

## 7. Pendientes y verificaciones omitidas

| Elemento | Estado | Motivo |
|---|---|---|
| Exportación a PDF | Diferido | Lo realizará el equipo a partir de estos Markdown. |
| Entrenamiento y métricas de modelos | Diferido | Planificado para Sprint 2 según `05_entrenamiento/config_entrenamiento.json`. |
| Implementación del flujo RAG | Diferido | Planificado para Sprint 2. |
| Pruebas unitarias de `ml_service/tests/` | No ejecutadas | La entrega no modificó el código canónico; la copia se verificó por SHA-256. |
