# Reporte de Pipeline de Transformación — HU-06

> Generado automáticamente por el pipeline de análisis de PredictMain.

---

## 1. Resumen Ejecutivo

| Métrica | Valor |
| :--- | :--- |
| Archivo analizado | `ai4i2020_outlier_analyzed.csv` |
| Fecha de ejecución | 2026-11-23 00:59:40 UTC |
| Registros de entrada | 10,000 |
| Registros usados en `fit` | 8,000 |
| Registros usados solo en `transform` | 2,000 |
| Registros transformados en salida | 10,000 |
| División | 80% / 20% estratificada (`random_state=42`) |
| Nulos en la matriz final | 0 |
| Artefacto serializado | `ml_service/artifacts/pipeline.joblib` |

> **Anti-leakage:** `StandardScaler` y `OneHotEncoder` se ajustaron únicamente con el conjunto de entrenamiento. El conjunto de prueba se transformó sin re-ajustar el pipeline.

---

## 2. Matriz de características final

8 predictoras: 5 sensores escalados, `Temp_diff` (derivada) y `Type_L` / `Type_M` (One-Hot con `Type_H` como referencia).

| # | Variable |
| :--- | :--- |
| 1 | `Air temperature [K]` |
| 2 | `Process temperature [K]` |
| 3 | `Rotational speed [rpm]` |
| 4 | `Torque [Nm]` |
| 5 | `Tool wear [min]` |
| 6 | `Temp_diff` |
| 7 | `Type_L` |
| 8 | `Type_M` |

Variable objetivo separada: `Machine failure`.

---

## 3. Columnas excluidas de la matriz

| Columna | Motivo |
| :--- | :--- |
| `UDI` | Identificador o etiqueta de falla posterior (leakage) |
| `Product ID` | Identificador o etiqueta de falla posterior (leakage) |
| `Machine failure` | Variable objetivo |
| `TWF` | Identificador o etiqueta de falla posterior (leakage) |
| `HDF` | Identificador o etiqueta de falla posterior (leakage) |
| `PWF` | Identificador o etiqueta de falla posterior (leakage) |
| `OSF` | Identificador o etiqueta de falla posterior (leakage) |
| `RNF` | Identificador o etiqueta de falla posterior (leakage) |

---

## 4. Trazabilidad de la división

| Parámetro | Valor |
| :--- | :--- |
| Estrategia | Estratificada |
| `test_size` | 0.2 |
| `random_state` | 42 |
| Filas de entrenamiento | 8,000 |
| Filas de prueba | 2,000 |

El CSV transformado conserva todas las filas para trazabilidad; la división se reproduce con `split_dataset()` y la misma semilla antes de entrenar el modelo.

---

## 5. Conclusión

El pipeline se ajustó solo con entrenamiento, transformó la prueba sin errores y quedó serializado para aplicar el mismo procesamiento a datos nuevos en producción.

---

> **Reporte generado:** 2026-11-23 00:59:40 UTC
