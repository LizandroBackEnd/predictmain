# Reporte de Validación de Matriz de Características — HU-07

> Generado automáticamente por el pipeline de análisis de PredictMain.

---

## 1. Dimensiones de la matriz

| Objeto | Shape |
| :--- | :--- |
| Matriz de predictoras `X` | `(10000, 8)` |
| Variable objetivo `y` | `(10000,)` |

Archivo validado: `ai4i2020_transformed.csv`.
Fecha de ejecución: 2026-11-23 00:59:40 UTC.

---

## 2. Verificación por criterio de aceptación

| # | Criterio | Resultado | Detalle |
| :--- | :--- | :--- | :--- |
| 1 | La matriz contiene las variables documentadas | ✔ | Esperadas 8; encontradas 8 |
| 2 | La variable objetivo está separada de las predictoras | ✔ | `Machine failure` ausente en X; y=(10000,) |
| 3 | No existen valores nulos inesperados | ✔ | 0 nulos en X e y |
| 4 | Los tipos de datos son compatibles con el modelo | ✔ | Todas las predictoras y el objetivo son numéricos |
| 5 | No existe fuga de información (data leakage) | ✔ | Sin identificadores, modos de falla ni objetivo en X |
| 6 | Las dimensiones quedan registradas para el reporte | ✔ | X=(10000, 8), y=(10000,) |

---

## 3. Conclusión

**Todas las verificaciones pasaron.** La matriz está lista para el entrenamiento.

Columnas de la matriz: `Air temperature [K]`, `Process temperature [K]`, `Rotational speed [rpm]`, `Torque [Nm]`, `Tool wear [min]`, `Temp_diff`, `Type_L`, `Type_M`.
Variable objetivo separada: `Machine failure`.

---

> **Reporte generado:** 2026-11-23 00:59:40 UTC
