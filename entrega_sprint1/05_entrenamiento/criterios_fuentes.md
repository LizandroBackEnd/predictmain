# Criterios de selección de fuentes

> Reglas para decidir qué documentos pueden formar parte del corpus del agente PredictMain.

## 1. Criterios obligatorios

| Criterio | Descripción |
| :--- | :--- |
| Autoridad | La fuente debe provenir del fabricante, un manual oficial, un procedimiento interno aprobado o una norma reconocida. |
| Relevancia | El contenido debe tratar mantenimiento, operación, seguridad o diagnóstico de la maquinaria monitoreada. |
| Vigencia | La versión debe ser la vigente o estar claramente identificada como histórica. |
| Trazabilidad | Debe conocerse el origen, la fecha, la versión y el responsable del documento. |
| Integridad | El documento debe estar completo y legible; no se aceptan fragmentos sin contexto. |
| Consistencia | No debe contradecir fuentes oficiales sin una justificación documentada. |
| Licencia | Su uso debe estar permitido para el propósito del proyecto. |
| Idioma | Se aceptan documentos en español o inglés; el agente responderá en español. |

## 2. Jerarquía de fuentes

| Nivel | Tipo de fuente | Prioridad |
| :--- | :--- | :--- |
| 1 | Manual del fabricante | Máxima |
| 2 | Procedimiento interno aprobado | Alta |
| 3 | Norma o estándar técnico | Alta |
| 4 | Bitácora de mantenimiento validada | Media |
| 5 | Ficha técnica del componente | Media |
| 6 | Documento de capacitación | Media |
| 7 | Nota informal o correo | Baja; solo con validación |

## 3. Criterios de exclusión

Se excluyen:

1. Documentos sin autor o sin versión.
2. Copias ilegibles o incompletas.
3. Contenido duplicado sin valor adicional.
4. Fuentes anónimas o no verificables.
5. Documentos con licencia incompatible.
6. Información obsoleta sin advertencia.
7. Contenido ajeno al dominio de mantenimiento.
8. Datos personales o información sensible no autorizada.

## 4. Metadatos mínimos por documento

| Campo | Obligatorio |
| :--- | :--- |
| Título | Sí |
| Autor o institución | Sí |
| Versión | Sí |
| Fecha | Sí |
| Tipo de documento | Sí |
| Idioma | Sí |
| Número de páginas | Sí |
| Responsable | Sí |
| Licencia | Sí |
| Ruta o identificador | Sí |

## 5. Metadatos mínimos por fragmento

| Campo | Obligatorio |
| :--- | :--- |
| Documento | Sí |
| Sección | Sí |
| Página | Sí |
| Texto | Sí |
| Versión | Sí |
| Tipo de contenido | Sí |

## 6. Criterios de calidad del texto

1. Texto extraído sin errores graves de codificación.
2. Sin encabezados o pies de página repetidos.
3. Sin tablas truncadas que cambien el significado.
4. Sin imágenes sin descripción cuando aporten información crítica.
5. Sin fragmentos vacíos o demasiado cortos.
6. Sin duplicados exactos.

## 7. Proceso de aceptación

1. Registrar el documento en el catálogo de fuentes.
2. Verificar los criterios obligatorios.
3. Extraer el texto.
4. Limpiar y normalizar.
5. Fragmentar.
6. Validar calidad.
7. Aprobar o rechazar con justificación.

## 8. Prioridad aplicada al corpus del Sprint 1

El corpus recibido es un documento técnico y académico. Su jerarquía interna es:

1. Ficha oficial del dataset AI4I 2020 y artículo introductorio.
2. Investigaciones académicas sobre modelos, desbalance y selección de características.
3. Conocimiento consolidado sobre datos, modelos y métricas.
4. Reglas de interpretación y riesgos técnicos.
5. Glosario y síntesis final.

Cuando se incorporen manuales de planta, se aplicará esta prioridad:

1. Manual de operación de la máquina.
2. Manual de mantenimiento.
3. Procedimiento de seguridad.
4. Fichas técnicas de componentes críticos.
5. Bitácoras de fallas y mantenimiento.
6. Guías de diagnóstico.

## 9. Uso combinado de corpus y dataset

El agente dispone de dos tipos de fuente y debe usarlas según la pregunta:

| Tipo de consulta | Fuente principal | Fuente de apoyo | Regla |
| --- | --- | --- | --- |
| Lectura de telemetría | Dataset/telemetría | Corpus | No inferir valores faltantes. |
| Riesgo de falla | Modelo | Telemetría y corpus | Mostrar probabilidad, umbral y factores. |
| Concepto o metodología | Corpus | Documentación del proyecto | Citar sección y página. |
| Interpretación de una variable | Corpus | Dataset | No confundir definición con medición. |
| Diagnóstico de modo de falla | Modelo y modos | Corpus | Aclarar que los modos son auxiliares. |
| Recomendación operativa | Corpus y modelo | Telemetría | No emitir órdenes; recomendar validación humana. |

Reglas de prioridad:

1. Para datos de una máquina específica, prevalece la telemetría observada.
2. Para resultados del proyecto, prevalece la salida del modelo con su versión.
3. Para conceptos, metodología y referencias, prevalece el corpus.
4. Si el corpus y el dataset se contradicen, mostrar ambas versiones y explicar la diferencia.
5. No usar el corpus para inventar telemetría ni el dataset para inventar citas.
6. Toda respuesta debe indicar qué fuente sostiene cada afirmación.

## 10. Estado

Los criterios están definidos y aplicados al corpus `PredictMain_Corpus_Contenido.pdf`. El corpus fue procesado y validado con 11 verificaciones de calidad. La implementación del pipeline RAG queda pendiente.
