# Estructura y características del corpus

## 1. Representación del corpus

El corpus se procesa en cuatro representaciones sucesivas:

| Etapa | Archivo | Contenido |
| --- | --- | --- |
| Fuente | `corpus_original/PredictMain_Corpus_Contenido.pdf` | Documento original de 26 páginas, sin modificaciones. |
| Extracción | `salidas/corpus_extraido.txt` | Texto por página con marcadores `===== PAGINA N =====`. |
| Extracción estructurada | `salidas/corpus_extraido.json` | Metadatos y texto de cada página. |
| Limpieza | `salidas/corpus_limpio.txt` | Texto normalizado, sin ruido y con separadores de párrafo. |
| Depuración | `salidas/corpus_procesado.txt` | Corpus final sin duplicados, con párrafos ajustados a 200 caracteres. |

## 2. Estructura física del PDF

| Característica | Valor |
| --- | --- |
| Páginas | 26 |
| Tamaño | 236,597 bytes |
| Formato | PDF generado con Chromium/Skia |
| Idioma | Español |
| Texto seleccionable | Sí |
| Imágenes dependientes del texto | No se identificaron como fuente principal |
| Tablas | Presentes como texto y filas |
| Numeración de secciones | 1 a 18 |

## 3. Estructura lógica

El documento combina seis tipos de unidades de contenido:

1. **Portada y datos académicos:** título, institución, asignatura, grupo e integrantes.
2. **Introducción y problema:** descripción del corpus y problemática del mantenimiento reactivo.
3. **Fichas de investigación:** cinco investigaciones con identificación, propósito, modelos, métricas, hallazgo principal, interpretación crítica y aplicación en PredictMain.
4. **Conocimiento consolidado:** datos, modelos, métricas, riesgos y reglas de interpretación.
5. **Material de referencia:** glosario, síntesis final, documentación primaria y catálogo de fuentes.
6. **Reglas numeradas:** recomendaciones y criterios metodológicos dentro de las secciones consolidadas.

## 4. Mapa de secciones

| Sección | Título | Aporte principal |
| --- | --- | --- |
| 1 | Descripción del corpus | Alcance, propósito y temas integrados. |
| 2 | Problema central del dominio | Costos del mantenimiento reactivo y necesidad de anticipación. |
| 3 | AI4I 2020 Predictive Maintenance Dataset | Variables, origen, limitaciones y pertinencia. |
| 4 | Investigación 1 | Comparación de modelos, balanceo y selección de características. |
| 5 | Investigación 2 | Modelos de machine learning y deep learning con AI4I 2020. |
| 6 | Investigación 3 | Escasez de datos, desbalance y selección de características. |
| 7 | Investigación 4 | Mantenimiento predictivo en Industry 4.0. |
| 8 | Investigación 5 | XGBoost y ventana deslizante para mejorar la predicción. |
| 9 | Comparación general | Síntesis comparativa de las investigaciones. |
| 10 | Conocimiento sobre los datos | Distribución, calidad, desbalance y variables. |
| 11 | Conocimiento sobre los modelos | Familias de modelos, ventajas y limitaciones. |
| 12 | Métricas de evaluación | Accuracy, precisión, recall, F1, ROC-AUC y matrices de confusión. |
| 13 | Riesgos técnicos | Fuga de información, sobreajuste, desbalance y datos sintéticos. |
| 14 | Reglas de interpretación | Criterios para usar el corpus en PredictMain. |
| 15 | Glosario técnico | Definiciones del dominio y de machine learning. |
| 16 | Síntesis final | Conclusiones aplicables al proyecto. |
| 17 | Documentación primaria | Fuente UCI y artículo introductorio de AI4I 2020. |
| 18 | Catálogo de fuentes | Referencias identificadas con enlaces. |

## 5. Estadísticas del procesamiento

| Métrica | Valor |
| --- | --- |
| Páginas extraídas | 26 |
| Caracteres extraídos | 54,903 |
| Caracteres después de limpieza | 40,285 |
| Caracteres del corpus procesado | 40,172 |
| Párrafos procesados | 469 |
| Secciones detectadas | 18 |
| Longitud promedio de párrafo | 83.7 caracteres |
| Longitud máxima de línea | 200 caracteres |
| Duplicados de párrafo eliminados | 4 |
| Duplicados de párrafo restantes | 0 |
| Verificaciones de calidad aprobadas | 11 de 11 |

## 6. Esquema de las unidades procesadas

Cada párrafo del archivo `corpus_procesado.txt` cumple estas reglas:

- Está separado del siguiente por una línea en blanco.
- Tiene un ancho máximo de 200 caracteres por línea.
- No contiene marcadores de página.
- No contiene caracteres decorativos como `•`, `·`, `|`, `_`, `*`, `=` o `{}`.
- Conserva tildes, signos de apertura y puntuación académica.
- Mantiene el orden original del documento.

## 7. Uso como fuente para RAG

Para la base de conocimiento del asistente, el corpus puede fragmentarse en unidades de 500 a 1,000 caracteres con solapamiento de 100 a 150 caracteres. Cada fragmento debe conservar:

| Campo | Descripción |
| --- | --- |
| `texto` | Contenido del párrafo o bloque. |
| `seccion` | Número y título de la sección de origen. |
| `fuente` | `PredictMain_Corpus_Contenido.pdf`. |
| `idioma` | `es`. |
| `tipo` | `corpus_tecnico`. |

La fragmentación debe respetar los límites de párrafo para no cortar ideas completas.

## 8. Correspondencia con los módulos del proyecto

| Módulo | Uso del corpus |
| --- | --- |
| `predictive-analytics` | Justificación de modelos, métricas y riesgos. |
| `telemetry-ingestion` | Interpretación de variables y umbrales operativos. |
| `knowledge-base` | Fuente documental para búsqueda semántica y RAG. |
| `assets-management` | Contexto de tipos de máquina y variables del dataset. |

## 9. Reproducibilidad

Dependencia:

```powershell
pip install -r 02_corpus/requirements.txt
```

Ejecución desde la raíz de `entrega_sprint1`:

```powershell
python 02_corpus/scripts/limpieza_normalizacion.py
python 02_corpus/scripts/depuracion_calidad.py
```

El primer script extrae el PDF y genera `salidas/corpus_extraido.txt`, `salidas/corpus_extraido.json` y `salidas/corpus_limpio.txt`. El segundo genera `salidas/corpus_procesado.txt` y las evidencias de depuración y calidad.
