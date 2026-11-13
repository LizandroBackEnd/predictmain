# Matriz de trazabilidad de requisitos de Sprint 1

Esta matriz relaciona cada entregable solicitado con el archivo de la entrega que
lo demuestra, con su fuente canónica y con la evidencia de validación. Las rutas
son relativas a `entrega_sprint1/`, salvo `data/` y `ml_service/`, que están en la
raíz del repositorio.

## 1. Requisitos y estado

| Requisito | Evidencia o entregable | Fuente canónica / referencia | Validación | Estado |
|---|---|---|---|---|
| Documento de Visión del Proyecto actualizado | `01_vision/vision_proyecto.md` | Alcance del producto y `data/raw/manifest.json` | Encabezados requeridos presentes (`01_vision/evidencias/verificacion_final_entrega.md`) | Verificado |
| Corpus original, procedencia y formato | `02_corpus/documentacion/corpus_original.md` | PDF original inmutable | SHA-256 del PDF sin cambios | Verificado |
| Estructura y características del corpus | `02_corpus/documentacion/estructura_corpus.md` | PDF original y `02_corpus/evidencias/reporte_limpieza_corpus.md` | Métricas coinciden con la ejecución | Verificado |
| Limpieza y normalización del corpus | `02_corpus/scripts/limpieza_normalizacion.py` | Reglas en `02_corpus/documentacion/criterios_calidad.md` | `02_corpus/evidencias/ejecucion_corpus.log` | Verificado |
| Eliminación de duplicados, caracteres irrelevantes y ruido | `02_corpus/scripts/depuracion_calidad.py` | `02_corpus/evidencias/reporte_depuracion_corpus.md` | 11 de 11 verificaciones en `02_corpus/evidencias/validacion_calidad_corpus.md` | Verificado |
| Evidencia del corpus procesado | `02_corpus/salidas/corpus_procesado.txt` y `02_corpus/evidencias/` | PDF original y ejecución reproducible | Sin marcadores ni ruido; PDF faltante o ilegible falla con error descriptivo | Verificado |
| Criterios de calidad del corpus | `02_corpus/documentacion/criterios_calidad.md` | `02_corpus/evidencias/validacion_calidad_corpus.md` | Un corpus defectuoso devuelve código 1 e indica el criterio fallido | Verificado |
| Limpieza y transformación del dataset | `03_dataset/ml_service/src/` | `ml_service/src/` | Copia idéntica por SHA-256 (`03_dataset/evidencias/reconciliacion_entrega.md`) | Verificado |
| Tratamiento de nulos, duplicados, inconsistencias y atípicos | `03_dataset/documentacion/limpieza_transformacion.md` y `03_dataset/reports/` | `ml_service/src/application/` | `03_dataset/evidencias/validacion_dataset.md` | Verificado |
| Normalización y transformación de variables | `03_dataset/data/processed/ai4i2020_transformed.csv` | `data/processed/ai4i2020_transformed.csv` | Reejecución idéntica byte a byte | Verificado |
| Dataset procesado y validado | `03_dataset/data/processed/` | `data/processed/` | 36 de 36 verificaciones de validación y 36 de 36 de reconciliación | Verificado |
| Evidencia de ejecución | `03_dataset/evidencias/pipeline_ejecucion.log` y `03_dataset/evidencias/validacion_dataset.log` | CLI canónica del pipeline | Cinco etapas con código 0 en una copia temporal limpia | Verificado |
| Comparativa antes/después | `03_dataset/evidencias/comparativa_datasets.md` | `03_dataset/scripts_evidencia/comparar_datasets.py` | Reproducible: dos ejecuciones producen el mismo archivo | Verificado |
| Catálogo de etiquetas y categorías | `04_etiquetado/catalogo_etiquetas.md` | Dataset AI4I 2020 | Valores de `etiqueta` y `modos_activos` validados contra el catálogo | Verificado |
| Reglas para asignar etiquetas | `04_etiquetado/reglas_etiquetado.md` | `04_etiquetado/scripts/validar_etiquetas.py` | 0 etiquetas contradictorias | Verificado |
| Muestra de registros etiquetados | `04_etiquetado/datos/muestra_etiquetada.csv` y `04_etiquetado/muestra_etiquetada.md` | `04_etiquetado/scripts/generar_muestra_etiquetada.py` | Semilla fija; 30 registros trazables al dataset completo | Verificado |
| Archivo con datos etiquetados | `04_etiquetado/datos/datos_etiquetados.csv` | `03_dataset/data/raw/ai4i2020.csv` | Columnas originales idénticas al crudo | Verificado |
| Validación de consistencia del etiquetado | `04_etiquetado/validacion_etiquetado.md` y `04_etiquetado/evidencias/validacion_etiquetado.log` | Scripts de etiquetado | 23 de 23 verificaciones | Verificado |
| Reglas y parámetros para entrenamiento/adaptación | `05_entrenamiento/reglas_parametros_entrenamiento.md` y `05_entrenamiento/config_entrenamiento.json` | `ml_service/` y arquitectura del proyecto | Parámetros de la configuración dentro de los rangos documentados | Verificado |
| Objetivo del entrenamiento | `05_entrenamiento/objetivo_modelo.md` | Visión del proyecto | Revisión de consistencia | Verificado |
| Estrategia seleccionada y justificación | `05_entrenamiento/estrategia_entrenamiento.md` | Arquitectura RAG + modelo supervisado | Revisión de consistencia | Verificado |
| System Prompt | `05_entrenamiento/system_prompt.md` | Reglas del agente PredictMain | Incluye abstención y prohíbe inventar datos, fuentes, probabilidades y citas | Verificado |
| Interpretación de consultas y respuestas | `05_entrenamiento/reglas_consulta_respuesta.md` | System Prompt | Incluye regla y ejemplo de evidencia insuficiente | Verificado |
| Criterios para usar corpus y dataset | `05_entrenamiento/criterios_fuentes.md` | Corpus y dataset canónicos | Separa salida del modelo, evidencia del corpus e inferencia del agente | Verificado |
| Scripts Python comentados | Scripts bajo `02_corpus/scripts/`, `03_dataset/scripts_evidencia/` y `04_etiquetado/scripts/` | Copias de `ml_service/src/` sin alterar | Docstrings y comentarios de las reglas no evidentes | Verificado |
| Documentación lista para exportar a PDF | Markdown completo en `entrega_sprint1/` | Exportación manual posterior | Sin referencias rotas ni PDF generados | Verificado |

## 2. Pendientes y omisiones justificadas

| Elemento | Motivo | Responsable de la siguiente acción |
|---|---|---|
| Exportación de la documentación a PDF | Se decidió entregar Markdown versionable; la exportación es una actividad posterior de presentación. | Equipo PredictMain, antes de la entrega formal |
| Entrenamiento de modelos y `05_entrenamiento/evidencias/metricas_modelos.md` | Sprint 1 define objetivo, estrategia y parámetros; la ejecución figura como `pending_execution` en `05_entrenamiento/config_entrenamiento.json`. | Equipo PredictMain, Sprint 2 |
| Implementación del flujo RAG y del agente | El diseño figura como `designed_pending_implementation`; la integración con pgvector y la API pertenece al núcleo Next.js. | Equipo PredictMain, Sprint 2 |

## 3. Conflictos detectados y resolución

| Conflicto | Artefacto canónico | Resolución |
|---|---|---|
| El CSV de entrega tenía SHA-256 `dc6630cd...` (522,048 bytes) y el canónico `59db4f1d...` (512,047 bytes). | `data/raw/ai4i2020.csv` | Se reemplazó la copia por la canónica. El contenido es idéntico: la diferencia son finales de línea CRLF frente a LF. Ver `03_dataset/documentacion/limpieza_transformacion.md`, sección 1.1. |
| `05_entrenamiento/config_entrenamiento.json` declaraba para el corpus procesado el SHA-256 `9CD37B95...`. | `02_corpus/salidas/corpus_procesado.txt` | Ese valor corresponde al archivo con finales CRLF. Se actualizó al SHA-256 del archivo entregado (`33C0B54C...`). |
| Esta matriz citaba `02_corpus/scripts/limpiar_corpus.py`, `02_corpus/documentacion/validacion_calidad.md` y `02_corpus/evidencias/validacion_calidad.log`, que no existen. | Archivos actuales de `02_corpus/` | Se corrigieron las referencias. |

## Criterio de aceptación

Un requisito se considera verificado cuando el archivo indicado existe, describe el
procedimiento aplicable, su script de validación termina con código 0 y sus cifras
o hashes coinciden con la línea base de
`01_vision/evidencias/inventario_fuentes_canonicas.md`. La exportación a PDF no
forma parte de esta implementación; los Markdown quedan preparados para que el
equipo los convierta posteriormente.
