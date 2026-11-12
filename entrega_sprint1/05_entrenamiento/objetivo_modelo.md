# Objetivo del modelo y del agente

## 1. Problema

Predecir si una lectura de telemetría industrial corresponde a una falla operativa de la máquina.

## 2. Tipo de problema

| Elemento | Definición |
| :--- | :--- |
| Tarea | Clasificación binaria supervisada |
| Variable objetivo | `Machine failure` |
| Clases | `0` = sin falla, `1` = falla |
| Unidad de predicción | Una lectura de telemetría |
| Momento de uso | Después de capturar las variables operativas y antes de la siguiente intervención |

## 3. Entradas del modelo

| Variable | Tipo | Descripción |
| :--- | :--- | :--- |
| `Air temperature [K]` | Continua | Temperatura ambiente. |
| `Process temperature [K]` | Continua | Temperatura del proceso. |
| `Rotational speed [rpm]` | Continua | Velocidad de rotación. |
| `Torque [Nm]` | Continua | Torque aplicado. |
| `Tool wear [min]` | Continua | Desgaste acumulado de herramienta. |
| `Temp_diff` | Continua derivada | Diferencia entre temperatura de proceso y ambiente. |
| `Type_L` | Binaria | Indicador One-Hot del tipo L. |
| `Type_M` | Binaria | Indicador One-Hot del tipo M. |

`Type_H` es la categoría de referencia y se omite.

## 4. Salida esperada

| Salida | Descripción |
| :--- | :--- |
| Probabilidad de falla | Valor continuo entre 0 y 1. |
| Clase predicha | `0` o `1` según el umbral seleccionado. |
| Nivel de riesgo | Bajo, medio o alto, derivado de la probabilidad. |
| Explicación | Variables con mayor contribución o contexto operativo. |

## 5. Métricas de éxito

| Métrica | Objetivo |
| :--- | :--- |
| Recall (clase falla) | Prioridad alta; minimizar falsos negativos. |
| Precision (clase falla) | Mantener un nivel aceptable para evitar alertas excesivas. |
| F1-score | Equilibrio entre precision y recall. |
| ROC-AUC | Capacidad de discriminación global. |
| PR-AUC | Desempeño ante desbalance de clases. |
| Matriz de confusión | Visualizar falsos positivos y falsos negativos. |

## 6. Restricciones

1. El modelo no debe usar `UDI` ni `Product ID`.
2. El modelo no debe usar los modos de falla como entradas.
3. El preprocesamiento debe ajustarse solo con datos de entrenamiento.
4. La partición debe ser reproducible.
5. El modelo debe manejar el desbalance de clases.
6. La salida debe ser interpretable para un técnico de mantenimiento.

## 7. Riesgos

| Riesgo | Mitigación |
| :--- | :--- |
| Desbalance de clases (3.39% fallas) | `class_weight`, métricas adecuadas y umbral ajustado. |
| Fuga de información | Excluir identificadores y modos de falla. |
| Sobreajuste | Validación cruzada y conjunto de prueba independiente. |
| Datos sintéticos | Documentar que AI4I es un dataset de referencia, no telemetría real. |
| Falsos negativos costosos | Priorizar recall y revisión humana. |
| Interpretación excesiva | El agente debe declarar incertidumbre y limitaciones. |

## 8. Criterio de aceptación del clasificador

El modelo se considera aceptable si:

1. Supera una línea base trivial.
2. Presenta recall razonable para la clase de falla.
3. No usa variables prohibidas.
4. Es reproducible con una semilla fija.
5. Sus resultados pueden explicarse con las variables de entrada.

## 9. Objetivo del agente LLM

El agente no se entrena para predecir fallas: se adapta para interpretar consultas y responder con evidencia. Su objetivo es:

| Elemento | Definición |
| --- | --- |
| Función | Asistente técnico de mantenimiento predictivo. |
| Entradas | Consulta, telemetría, salida del clasificador y fragmentos del corpus. |
| Salidas | Respuesta en español con datos, riesgo, evidencia, recomendación y limitaciones. |
| Estrategia | RAG + Prompt Engineering. |
| Conocimiento | Corpus PredictMain procesado y validado. |
| Límite | No inventa datos, no emite órdenes y no reemplaza al especialista. |

### 9.1 Criterios de aceptación del agente

1. Distingue datos observados, modelo, corpus e inferencia.
2. Cita documento, sección y página cuando están disponibles.
3. Reconoce evidencia insuficiente.
4. No inventa lecturas ni fuentes.
5. Escala a un humano cuando el riesgo es alto o hay contradicciones.
6. Responde en español técnico y con formato claro.

### 9.2 Relación entre clasificador y agente

El clasificador produce la probabilidad de falla. El agente la interpreta junto con la telemetría y el corpus. El agente no recalcula el modelo ni sustituye su salida; si el modelo no está disponible, debe declararlo y responder solo con la evidencia documental.
