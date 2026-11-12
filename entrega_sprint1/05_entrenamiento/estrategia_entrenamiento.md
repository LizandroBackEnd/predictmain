# Estrategia de entrenamiento y adaptación

> Plan para el modelo de riesgo de falla y para la adaptación del agente LLM de PredictMain.

## 1. Alcance

La estrategia cubre dos componentes con ciclos de vida distintos:

| Componente | Objetivo | Estrategia |
| --- | --- | --- |
| Modelo predictivo | Estimar la probabilidad de falla a partir de telemetría. | Entrenamiento supervisado clásico. |
| Agente LLM | Interpretar consultas y responder con evidencia documental. | RAG + Prompt Engineering. |

El clasificador y el agente se evalúan por separado. El agente consume la salida del clasificador, pero no la recalcula ni la inventa.

## 2. Modelo predictivo

### 2.1 Datos de entrada

| Elemento | Valor |
| --- | --- |
| Archivo | `03_dataset/data/processed/ai4i2020_transformed.csv` |
| Registros | 10,000 |
| Variables de entrada | 8 |
| Variable objetivo | `Machine failure` |
| Fallas | 339 (3.39%) |
| Sin falla | 9,661 (96.61%) |

### 2.2 Partición

| Conjunto | Proporción | Registros aproximados |
| --- | --- | --- |
| Entrenamiento | 70% | 7,000 |
| Validación | 15% | 1,500 |
| Prueba | 15% | 1,500 |

- **Estratificación:** por `Machine failure` y `Type`.
- **Semilla:** `random_state=42`.
- **Regla:** el conjunto de prueba no se usa para ajustar el modelo ni el umbral.

### 2.3 Preprocesamiento

1. `Temp_diff = Process temperature - Air temperature`.
2. `StandardScaler` sobre las cinco variables continuas y `Temp_diff`.
3. `OneHotEncoder(drop='first')` sobre `Type`.
4. Exclusión de identificadores y modos de falla.

El escalador y el codificador se ajustan solo con el conjunto de entrenamiento.

### 2.4 Modelos candidatos

| Modelo | Rol | Ventaja |
| --- | --- | --- |
| Regresión logística | Línea base interpretable | Coeficientes claros y rápida |
| Random Forest | Modelo no lineal | Robusto y captura interacciones |
| Gradient Boosting | Modelo de alto desempeño | Buen rendimiento tabular |
| HistGradientBoosting | Alternativa eficiente | Manejo nativo de datos tabulares |

### 2.5 Manejo del desbalance

1. Usar `class_weight='balanced'` cuando el modelo lo permita.
2. Evaluar con precision, recall, F1, ROC-AUC y PR-AUC.
3. Ajustar el umbral de decisión en validación, priorizando recall.
4. No aplicar SMOTE en la primera iteración; evaluar solo si el recall es insuficiente.
5. Reportar la matriz de confusión con conteos absolutos.

### 2.6 Validación y métricas

- Validación cruzada estratificada de 5 particiones sobre entrenamiento.
- Selección de hiperparámetros con búsqueda acotada.
- Evaluación final única sobre el conjunto de prueba.
- Registro de semilla, versión de datos y versión de librerías.

| Métrica | Uso |
| --- | --- |
| Recall | Minimizar fallas no detectadas. |
| Precision | Controlar falsas alarmas. |
| F1 | Equilibrio general. |
| ROC-AUC | Discriminación global. |
| PR-AUC | Desempeño con clases desbalanceadas. |
| Matriz de confusión | Visualizar falsos positivos y falsos negativos. |

El umbral inicial será `0.5`. Se ajustará en validación buscando el mejor equilibrio entre recall y precision. El umbral final se documentará junto con el modelo.

### 2.7 Experimentos mínimos

| Experimento | Descripción |
| --- | --- |
| E1 | Regresión logística con `class_weight='balanced'`. |
| E2 | Random Forest con `class_weight='balanced'`. |
| E3 | Gradient Boosting. |
| E4 | HistGradientBoosting. |
| E5 | Mejor modelo con umbral ajustado. |

## 3. Agente LLM

### 3.1 Decisión de estrategia

| Estrategia | Aplicación en PredictMain | Decisión |
| --- | --- | --- |
| Prompt Engineering | Definir conducta, formato, límites y reglas de citación. | **Sí** |
| RAG | Recuperar fragmentos del corpus procesado y citar fuentes. | **Sí**, estrategia principal |
| Fine-tuning | Ajustar el modelo con pares consulta-respuesta. | **No** en Sprint 1 |
| Ajuste de umbral | Mejorar recall del clasificador sin reentrenar. | **Sí** |

La estrategia elegida es **RAG + Prompt Engineering**. El corpus tiene 40,172 caracteres procesados y 18 secciones; es suficientemente pequeño para recuperarlo por fragmentos y suficientemente cambiante para no justificar un fine-tuning. Además, no existe un dataset supervisado de consultas y respuestas del dominio.

### 3.2 Flujo RAG

```text
Consulta
  -> interpretación y clasificación
  -> búsqueda semántica en el corpus
  -> recuperación de 4 a 6 fragmentos
  -> incorporación de telemetría y salida del modelo (si aplica)
  -> generación con system prompt
  -> respuesta con citas y limitaciones
```

### 3.3 Parámetros de recuperación y generación

| Parámetro | Valor propuesto |
| --- | --- |
| Fragmentación | 500 a 1,000 caracteres |
| Solapamiento | 100 a 150 caracteres |
| Fragmentos recuperados | 4 a 6 |
| Similitud | Coseno |
| Temperatura | 0.1 a 0.3 |
| Máximo de tokens | 800 a 1,200 |
| Idioma | Español |
| Citación | Documento, sección y página |
| Abstención | "No tengo evidencia suficiente" |

### 3.4 Prompt Engineering

El system prompt define:

1. Función del agente y alcance.
2. Separación entre datos observados, modelo, corpus e inferencia.
3. Reglas de citación y abstención.
4. Formato de respuesta.
5. Criterios de escalamiento humano.
6. Prohibiciones de seguridad.

Las reglas de interpretación de consultas y generación de respuestas se detallan en `reglas_consulta_respuesta.md`.

## 4. Entregables

1. Script de entrenamiento reproducible del clasificador.
2. Modelo serializado y versión de datos.
3. Reporte de métricas por experimento.
4. Matriz de confusión y curvas del modelo seleccionado.
5. Documento de decisión del modelo final.
6. Implementación del pipeline RAG y del system prompt.
7. Evaluación de fidelidad y trazabilidad del agente.

## 5. Reproducibilidad

```text
Semilla: 42
Partición: estratificada
Preprocesamiento: pipeline reproducible desde scripts
Corpus: PredictMain_Corpus_Contenido.pdf (SHA-256 verificado)
Versiones: registrar Python, pandas, scikit-learn, joblib y modelo LLM
```

## 6. Estado

- Modelo predictivo: **definido, pendiente de ejecución**.
- Corpus: **procesado y validado**.
- Agente RAG: **diseñado, pendiente de implementación**.
- Fine-tuning: **descartado para Sprint 1**.
