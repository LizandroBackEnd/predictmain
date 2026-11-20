# Visión del proyecto PredictMain

## 1. Identificación

- **Proyecto:** PredictMain
- **Institución:** Universidad Tecnológica de Nezahualcóyotl (UTN)
- **Carrera:** Licenciatura en Ingeniería en Tecnologías de la Información e Innovación Digital
- **Asignatura:** Formulación de Proyectos de Tecnología
- **Equipo:** Antonio Santos Lizandro, Baez García Fátima Guadalupe, Bautista Patiño Luis Antonio, Cruz Jaime Jessica Beatriz, Mérida López María Isabel.
- **Sprint:** Sprint 1 - Agente de IA para mantenimiento predictivo.

## 2. Problema

Las pequeñas y medianas empresas industriales suelen aplicar mantenimiento reactivo o basado en calendarios fijos. Esto produce:

1. Paros no planificados y pérdidas económicas.
2. Telemetría dispersa o registrada manualmente.
3. Decisiones sin indicadores objetivos de desgaste.
4. Dificultad para consultar manuales, historiales y procedimientos técnicos.

## 3. Propuesta de valor

PredictMain convierte lecturas de telemetría en indicadores accionables de riesgo de falla y complementa la operación con un asistente técnico basado en recuperación de conocimiento (RAG).

El agente de IA debe:

- Interpretar variables operativas de maquinaria industrial.
- Estimar el riesgo de falla a partir de un modelo supervisado.
- Explicar el resultado en lenguaje técnico claro.
- Recuperar información de manuales y bitácoras para responder consultas.
- Citar las fuentes utilizadas.
- Alertar cuando la evidencia sea insuficiente o contradictoria.

## 4. Objetivos

### 4.1 Objetivo general

Desarrollar una plataforma web de mantenimiento predictivo que utilice telemetría y técnicas de análisis e inteligencia artificial para estimar el desgaste y el riesgo de falla de maquinaria industrial.

### 4.2 Objetivos específicos del Sprint 1

1. Documentar la visión y el alcance del agente.
2. Preparar y validar el dataset AI4I 2020.
3. Documentar el proceso de limpieza, transformación y etiquetado.
4. Definir las variables de entrada y la variable objetivo del modelo.
5. Definir la estrategia de entrenamiento y evaluación.
6. Diseñar el system prompt y las reglas de comportamiento del agente.
7. Definir los criterios de selección de fuentes para el corpus.
8. Procesar, depurar y validar el corpus documental del proyecto.

## 5. Alcance

### 5.1 Incluido en el Sprint 1

- Dataset crudo, limpio, analizado y transformado.
- Pipeline reproducible de datos.
- Reportes de perfilado, nulos y atípicos.
- Catálogo y reglas de etiquetado.
- Dataset etiquetado completo y muestra de revisión.
- Corpus documental procesado y validado.
- Documentación del modelo y del agente.
- Criterios de fuentes y system prompt.

### 5.2 No incluido en el Sprint 1

- Base vectorial y embeddings.
- Asistente RAG implementado en producción.
- Entrenamiento y despliegue del modelo final.
- Aplicación web y dashboards.
- Validación formal con especialistas de dominio.
- Fragmentación definitiva del corpus para recuperación semántica.

## 6. Usuarios

| Usuario | Necesidad |
| :--- | :--- |
| Técnico de mantenimiento | Conocer el riesgo de falla y priorizar intervenciones. |
| Supervisor de planta | Consultar tendencias, alertas e historial. |
| Ingeniero de confiabilidad | Analizar desgaste y modos de falla. |
| Administrador | Gestionar activos, usuarios y catálogos. |
| Especialista de dominio | Validar etiquetas y recomendaciones. |

## 7. Arquitectura de referencia

PredictMain se organiza en dos componentes desacoplados:

```text
Next.js 16 + TypeScript + Bun
  -> Interfaz web, activos, telemetría, reportes y asistente RAG.
  -> Comunicación HTTP con el servicio de ML.

Python 3.11 + FastAPI + Scikit-learn
  -> Perfilado, limpieza, transformación, entrenamiento e inferencia.
  -> Artefactos serializados en ml_service/artifacts/.
```

El agente no ejecuta código Python directamente. Consume resultados del modelo y del corpus mediante interfaces HTTP y fuentes documentales controladas.

## 8. Datos de referencia

- **Dataset:** AI4I 2020 Predictive Maintenance Dataset.
- **Registros:** 10,000.
- **Variables originales:** 14.
- **Variable objetivo:** `Machine failure`.
- **Fallas:** 339.
- **Variables de entrada del modelo:** 8.

### 8.1 Corpus documental

- **Documento:** `PredictMain_Corpus_Contenido.pdf`.
- **Páginas:** 26.
- **Secciones temáticas:** 18.
- **Texto procesado:** 40,172 caracteres.
- **Párrafos:** 469.
- **Estado:** procesado y validado con 11 verificaciones de calidad.

## 9. Criterios de éxito del Sprint 1

1. El pipeline se ejecuta sin errores y genera todos los artefactos.
2. El dataset procesado conserva 10,000 registros y 339 fallas.
3. Las etiquetas están documentadas y validadas.
4. La muestra etiquetada es reproducible.
5. La estrategia de entrenamiento es clara y verificable.
6. El system prompt define reglas, límites y formato de respuesta.
7. El corpus se procesa y valida con evidencia reproducible.
8. Los pendientes están identificados y justificados.

## 10. Trazabilidad de la entrega

La relación completa entre los requisitos solicitados, los scripts, los datos
generados y sus evidencias se encuentra en
`01_vision/matriz_trazabilidad_requisitos.md`. La línea base de hashes, tamaños,
esquemas y fuentes inmutables se encuentra en
`01_vision/evidencias/inventario_fuentes_canonicas.md`.

La entrega utiliza como fuentes canónicas el contenido de `data/` y
`ml_service/`. Las copias dentro de `entrega_sprint1/` son artefactos de
distribución y deben conservar la misma información verificable. La conversión
de esta documentación a PDF se realizará posteriormente como actividad de
entrega, fuera del alcance de este cambio.
