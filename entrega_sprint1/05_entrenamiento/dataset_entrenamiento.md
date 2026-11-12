# Dataset de entrenamiento

## 1. Archivo

| Elemento | Valor |
| :--- | :--- |
| Ruta | `03_dataset/data/processed/ai4i2020_transformed.csv` |
| Registros | 10,000 |
| Columnas | 9 |
| Variables de entrada | 8 |
| Variable objetivo | `Machine failure` |
| Nulos | 0 |
| Duplicados | 0 |

## 2. Esquema

| Columna | Tipo | Rol |
| :--- | :--- | :--- |
| `Air temperature [K]` | float | Entrada |
| `Process temperature [K]` | float | Entrada |
| `Rotational speed [rpm]` | float | Entrada |
| `Torque [Nm]` | float | Entrada |
| `Tool wear [min]` | float | Entrada |
| `Temp_diff` | float | Entrada derivada |
| `Type_L` | int | Entrada One-Hot |
| `Type_M` | int | Entrada One-Hot |
| `Machine failure` | int | Objetivo |

## 3. Distribución de clases

| Clase | Registros | Porcentaje |
| :--- | :--- | :--- |
| 0 (sin falla) | 9,661 | 96.61% |
| 1 (falla) | 339 | 3.39% |

## 4. Prevención de fuga de información

No se usan como entradas:

- `UDI`.
- `Product ID`.
- `TWF`, `HDF`, `PWF`, `OSF`, `RNF`.
- `Type` original (se reemplaza por `Type_L` y `Type_M`).

## 5. Origen de las variables

| Variable | Origen |
| :--- | :--- |
| Cinco sensores | Dataset AI4I 2020. |
| `Temp_diff` | Derivada: `Process temperature - Air temperature`. |
| `Type_L`, `Type_M` | One-Hot Encoding de `Type` con `drop='first'`. |
| `Machine failure` | Etiqueta original. |

## 6. Partición recomendada

| Conjunto | Proporción |
| :--- | :--- |
| Entrenamiento | 70% |
| Validación | 15% |
| Prueba | 15% |

La partición debe ser estratificada por `Machine failure` y `Type`, con semilla `42`.

## 7. Artefactos relacionados

| Artefacto | Ruta |
| :--- | :--- |
| Pipeline de preprocesamiento | `03_dataset/ml_service/artifacts/pipeline.joblib` |
| Dataset transformado | `03_dataset/data/processed/ai4i2020_transformed.csv` |
| Comparativa de datasets | `03_dataset/evidencias/comparativa_datasets.md` |
| Validación del dataset | `03_dataset/evidencias/validacion_dataset.md` |

## 8. Limitaciones

1. El dataset es sintético y de referencia; no representa telemetría real de una planta.
2. El desbalance de clases es alto.
3. Existen 27 inconsistencias entre la etiqueta y los modos de falla.
4. El modelo debe validarse con datos reales antes de usarse en producción.

## 9. Estado

**Dataset listo para entrenamiento.** La partición y el entrenamiento quedan pendientes de ejecución.
