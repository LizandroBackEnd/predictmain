# Criterios de calidad del corpus

## 1. Objetivo

Definir los criterios verificables para aceptar el corpus procesado como fuente documental de PredictMain. La calidad se evalúa en tres momentos: extracción, limpieza y depuración final.

## 2. Dimensiones de calidad

| Dimensión | Pregunta de control | Evidencia |
| --- | --- | --- |
| Integridad | ¿El archivo original se conserva sin cambios? | Hash SHA-256 y PDF original. |
| Completitud | ¿Se recuperó el contenido de las 26 páginas? | Conteo de páginas y caracteres extraídos. |
| Limpieza | ¿Se eliminaron ruido, encabezados y caracteres de control? | Reporte de limpieza. |
| Consistencia | ¿El texto mantiene una representación uniforme? | Normalización Unicode y espacios. |
| No redundancia | ¿Se eliminaron párrafos duplicados? | Reporte de depuración. |
| Relevancia | ¿El contenido pertenece al dominio de mantenimiento predictivo? | Palabras clave y secciones temáticas. |
| Usabilidad | ¿El texto puede consumirse por un pipeline RAG? | Párrafos, longitud de línea y formato UTF-8. |
| Trazabilidad | ¿Cada afirmación puede rastrearse a una sección o fuente? | Mapa de secciones y catálogo de fuentes. |

## 3. Criterios de aceptación

| Criterio | Umbral | Resultado | Estado |
| --- | --- | --- | --- |
| Corpus procesado no vacío | Más de 0 caracteres | 40,172 caracteres | OK |
| Conservación del texto limpio | Al menos 75% | 99.72% | OK |
| Marcadores de página | 0 | 0 | OK |
| Caracteres decorativos | 0 | 0 | OK |
| Carácter de reemplazo | 0 | 0 | OK |
| Párrafos duplicados restantes | 0 | 0 | OK |
| Secciones temáticas detectadas | Al menos 15 | 18 | OK |
| Párrafos procesados | Al menos 50 | 469 | OK |
| Longitud promedio de párrafo | Entre 30 y 1,200 caracteres | 83.7 caracteres | OK |
| Longitud máxima de línea | Menor o igual a 220 caracteres | 200 caracteres | OK |
| Palabras clave del dominio | Todas presentes | 6 de 6 | OK |

Resultado global: **11 de 11 verificaciones aprobadas**.

## 4. Reglas de limpieza aplicadas

1. **Codificación:** lectura y escritura en UTF-8.
2. **Normalización Unicode:** forma NFKC para unificar caracteres equivalentes.
3. **Caracteres invisibles:** eliminación de espacios de ancho cero, BOM y controles.
4. **Espacios:** colapso de espacios repetidos y eliminación de espacios al inicio y al final.
5. **Marcadores de página:** eliminación de líneas `===== PAGINA N =====`.
6. **Números de página:** eliminación de líneas compuestas solo por un número.
7. **Encabezados repetidos:** eliminación de líneas que se repiten en al menos la mitad de las páginas.
8. **Puntuación aislada:** eliminación de líneas compuestas solo por signos.
9. **Guiones de corte:** unión de palabras separadas por guion al final de línea cuando corresponde.
10. **Separadores de párrafo:** conservación de una línea en blanco entre bloques.
11. **Caracteres decorativos:** eliminación de `•`, `·`, `|`, `_`, `*`, `=`, `<`, `>`, `{` y `}`.
12. **Duplicados:** eliminación de párrafos idénticos y de líneas largas repetidas.
13. **Ancho de línea:** ajuste de párrafos a 200 caracteres para facilitar la fragmentación.
14. **Contenido irrelevante:** no se eliminó contenido temático porque las 18 secciones son relevantes para mantenimiento predictivo. La depuración se limitó a ruido de formato, duplicados y caracteres no deseados.

## 5. Métricas del proceso de limpieza

| Métrica | Valor |
| --- | --- |
| Caracteres extraídos | 54,903 |
| Caracteres después de limpieza | 40,285 |
| Porcentaje conservado en limpieza | 73.37% |
| Líneas de entrada | 1,224 |
| Líneas vacías eliminadas | 520 |
| Números de página eliminados | 1 |
| Encabezados repetidos eliminados | 0 |
| Líneas de solo puntuación eliminadas | 0 |
| Líneas con espacios colapsados | 318 |
| Guiones de corte unidos | 0 |

Nota: el porcentaje conservado en la limpieza es menor que el 75% porque se eliminan espacios de maquetación, saltos de página y líneas vacías. La validación final conserva el 99.72% del texto limpio.

## 6. Métricas del proceso de depuración

| Métrica | Valor |
| --- | --- |
| Caracteres de entrada | 40,285 |
| Caracteres de salida | 40,172 |
| Porcentaje conservado | 99.72% |
| Duplicados de párrafo eliminados | 4 |
| Duplicados de párrafo restantes | 0 |
| Duplicados de línea eliminados | 0 |
| Párrafos finales | 469 |

## 7. Validación de relevancia

Se verificó la presencia de términos centrales del dominio:

| Palabra clave | Presente |
| --- | --- |
| AI4I 2020 | Sí |
| Machine failure | Sí |
| Mantenimiento predictivo | Sí |
| Desbalance | Sí |
| Métricas | Sí |
| Características | Sí |

La presencia de estos términos no sustituye una revisión humana, pero confirma que el corpus conserva el vocabulario técnico necesario para el proyecto.

## 8. Criterios de rechazo

El corpus se rechaza o se reprocesa si ocurre cualquiera de estas condiciones:

- El PDF original fue modificado.
- La extracción produce menos de 20 páginas.
- El texto procesado contiene el carácter de reemplazo Unicode U+FFFD.
- Quedan marcadores de página en el texto final.
- Se detectan párrafos duplicados en la salida.
- Se pierde más del 25% del texto limpio.
- No se detectan al menos 15 secciones temáticas.
- Faltan palabras clave esenciales del dominio.
- El archivo final no puede leerse como UTF-8.

## 9. Limitaciones y revisión manual

La validación automática no detecta errores semánticos, omisiones de contenido ni errores de interpretación. Por ello se recomienda:

1. Revisar manualmente la portada, las 18 secciones y el catálogo de fuentes.
2. Contrastar las referencias del catálogo con sus documentos primarios.
3. Verificar que las tablas conserven filas y columnas legibles.
4. Revisar que las reglas numeradas no se hayan mezclado con párrafos.
5. Confirmar que el texto procesado no incluya fragmentos de otras fuentes.

## 10. Evidencias

| Evidencia | Archivo |
| --- | --- |
| Reporte de limpieza | `02_corpus/evidencias/reporte_limpieza_corpus.md` |
| Reporte de depuración | `02_corpus/evidencias/reporte_depuracion_corpus.md` |
| Validación de calidad | `02_corpus/evidencias/validacion_calidad_corpus.md` |
| Log de ejecución | `02_corpus/evidencias/ejecucion_corpus.log` |
| Corpus extraído | `02_corpus/salidas/corpus_extraido.txt` |
| Corpus limpio | `02_corpus/salidas/corpus_limpio.txt` |
| Corpus procesado | `02_corpus/salidas/corpus_procesado.txt` |
