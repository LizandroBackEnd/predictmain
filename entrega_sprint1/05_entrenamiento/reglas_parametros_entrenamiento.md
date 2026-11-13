# Reglas y parámetros de entrenamiento y adaptación

## 1. Alcance

Este documento define las reglas y los parámetros para dos componentes:

1. **Modelo predictivo:** clasificador binario de riesgo de falla.
2. **Agente LLM:** adaptación mediante RAG y Prompt Engineering, sin fine-tuning en el Sprint 1.

## 2. Reglas generales

1. El conjunto de prueba no se usa para ajustar el modelo, el umbral ni el prompt.
2. El preprocesamiento se ajusta solo con el conjunto de entrenamiento.
3. Toda partición debe ser estratificada y reproducible con semilla `42`.
4. No se usan identificadores ni modos de falla como variables de entrada.
5. Toda métrica debe reportarse con su umbral y matriz de confusión.
6. Toda respuesta del agente debe citar la evidencia recuperada.
7. Los cambios de prompt, modelo o corpus deben registrarse con versión y fecha.
8. No se acepta una mejora que dependa de fuga de información.

## 3. Parámetros del modelo predictivo

| Parámetro | Valor | Justificación |
| --- | --- | --- |
| Tarea | Clasificación binaria | `Machine failure` es 0/1. |
| Variable objetivo | `Machine failure` | Etiqueta oficial del dataset. |
| Variables de entrada | 8 | Cinco sensores, `Temp_diff`, `Type_L`, `Type_M`. |
| Partición | 70% entrenamiento, 15% validación, 15% prueba | Permite ajuste y evaluación independiente. |
| Estratificación | `Machine failure` y `Type` | Conserva proporciones de clases y tipos. |
| Semilla | `42` | Reproducibilidad. |
| Validación cruzada | `StratifiedKFold`, 5 particiones | Estabilidad con clases desbalanceadas. |
| Desbalance | `class_weight='balanced'` cuando aplique | Evita ignorar la clase minoritaria. |
| Umbral inicial | `0.5` | Punto de partida; se ajusta en validación. |
| Prioridad de umbral | Recall | Una falla no detectada es más costosa. |
| Métricas | Precision, recall, F1, ROC-AUC, PR-AUC, matriz de confusión | Evaluación completa del desbalance. |
| Modelos candidatos | Regresión logística, Random Forest, Gradient Boosting, HistGradientBoosting | Comparación de líneas base e modelos no lineales. |

## 4. Parámetros de adaptación del LLM

| Parámetro | Valor propuesto | Justificación |
| --- | --- | --- |
| Estrategia | RAG + Prompt Engineering | El corpus es pequeño y cambiante; no hay dataset de instrucciones. |
| Fine-tuning | No en Sprint 1 | Requiere datos supervisados de consulta-respuesta y mayor costo. |
| Fragmentación | 500 a 1,000 caracteres | Equilibrio entre contexto y precisión. |
| Solapamiento | 100 a 150 caracteres | Evita cortar ideas entre fragmentos. |
| Recuperación | 4 a 6 fragmentos | Suficiente contexto sin saturar la ventana. |
| Similitud | Coseno sobre embeddings | Estándar para búsqueda semántica. |
| Temperatura | 0.1 a 0.3 | Respuestas técnicas estables y poco creativas. |
| Máximo de tokens | 800 a 1,200 | Respuestas completas sin divagación. |
| Idioma de respuesta | Español | Idioma del usuario y del corpus. |
| Citación | Documento, sección y página | Trazabilidad académica. |
| Abstención | "No tengo evidencia suficiente" | Evita alucinaciones. |
| Evaluación | Fidelidad, trazabilidad, claridad, seguridad y utilidad | Criterios del agente. |

Los valores iniciales dentro de cada rango están fijados en `config_entrenamiento.json`: fragmentos de 800 caracteres, solapamiento de 120, 5 fragmentos recuperados, temperatura 0.2 y 1,000 tokens máximos.

## 5. Decisión de estrategia

| Estrategia | Evaluación | Decisión |
| --- | --- | --- |
| Prompt Engineering | Necesario para definir conducta, formato y límites. | **Sí**, como base. |
| RAG | Permite usar el corpus sin reentrenar y citar fuentes. | **Sí**, estrategia principal. |
| Fine-tuning | No hay dataset de pares consulta-respuesta; el corpus cambia. | **No** en Sprint 1. |
| Ajuste de umbral | Mejora recall sin reentrenar. | **Sí**, en validación. |

La combinación elegida es **RAG + Prompt Engineering** para el agente y **entrenamiento supervisado clásico** para el clasificador.

## 6. Flujo de adaptación del agente

```text
Consulta
  -> interpretación y clasificación
  -> búsqueda de fragmentos en el corpus
  -> recuperación de telemetría y salida del modelo (si aplica)
  -> construcción del contexto
  -> generación con system prompt y reglas
  -> respuesta con citas y limitaciones
```

## 7. Reglas de contexto

1. Incluir solo fragmentos recuperados y autorizados.
2. Ordenar los fragmentos por relevancia.
3. Etiquetar cada fragmento con documento, sección y página.
4. No incluir documentos completos si exceden la ventana.
5. Si dos fragmentos se contradicen, incluir ambos y señalarlo.
6. No usar el corpus para inventar telemetría ni resultados del modelo.

## 8. Evaluación

| Componente | Métrica | Criterio |
| --- | --- | --- |
| Clasificador | Recall de falla | Prioridad alta; comparar contra línea base. |
| Clasificador | PR-AUC | Desempeño con desbalance. |
| Clasificador | Matriz de confusión | Conteos absolutos de FP y FN. |
| Agente | Fidelidad | Ninguna afirmación sin respaldo. |
| Agente | Trazabilidad | Citas verificables. |
| Agente | Abstención | Reconoce evidencia insuficiente. |
| Agente | Seguridad | No emite órdenes ni oculta incertidumbre. |

## 9. Reproducibilidad

```text
Semilla: 42
Partición: estratificada
Preprocesamiento: pipeline reproducible desde scripts
Corpus: PredictMain_Corpus_Contenido.pdf (SHA-256 verificado)
Versiones: registrar Python, pandas, scikit-learn, joblib y modelo LLM
```

## 10. Estado

- Modelo predictivo: **definido, pendiente de ejecución**.
- Corpus: **procesado y validado**.
- Agente RAG: **diseñado, pendiente de implementación**.
- Fine-tuning: **descartado para Sprint 1**.
