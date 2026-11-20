# Comparativa de datasets del pipeline

Generado automáticamente por `scripts_evidencia/comparar_datasets.py`.

## 1. Resumen por etapa

| Etapa | Archivo | Filas | Columnas | Nulos | Duplicados | Fallas |
| --- | --- | --- | --- | --- | --- | --- |
| Crudo | ai4i2020.csv | 10,000 | 14 | 0 | 0 | 339 |
| Limpio (HU-04) | ai4i2020_clean.csv | 10,000 | 14 | 0 | 0 | 339 |
| Atípicos analizados (HU-05) | ai4i2020_outlier_analyzed.csv | 10,000 | 14 | 0 | 0 | 339 |
| Transformado (HU-06) | ai4i2020_transformed.csv | 10,000 | 9 | 0 | 0 | 339 |

## 2. Verificaciones de integridad

| Verificación | Resultado | Detalle |
| --- | --- | --- |
| Filas conservadas en limpieza | OK | 10,000 de 10,000 |
| Columnas conservadas en limpieza | OK | 14 columnas |
| Etiqueta objetivo idéntica tras limpieza | OK | 339 fallas |
| Filas conservadas tras análisis de atípicos | OK | 10,000 de 10,000 |
| Filas conservadas tras transformación | OK | 10,000 de 10,000 |
| Etiqueta objetivo idéntica tras transformación | OK | 339 fallas |
| Variables de entrada del modelo | OK | 8 variables |
| Sin valores nulos en la salida | OK | 0 nulos |
| Todos los cambios de columnas son intencionales | OK | 0 cambios no documentados |
| Valores sin modificar en limpieza | OK | 0 celdas modificadas |
| Valores sin modificar en análisis de atípicos | OK | 0 celdas modificadas |

## 3. Distribución de la variable objetivo

| Clase | Registros | Porcentaje |
| --- | --- | --- |
| 0 (sin falla) | 9,661 | 96.61% |
| 1 (falla) | 339 | 3.39% |

## 4. Distribución por tipo de producto

| Tipo | Registros | Porcentaje |
| --- | --- | --- |
| L | 6,000 | 60.00% |
| M | 2,997 | 29.97% |
| H | 1,003 | 10.03% |

## 5. Modos de falla registrados

| Modo | Registros |
| --- | --- |
| TWF | 46 |
| HDF | 115 |
| PWF | 95 |
| OSF | 98 |
| RNF | 19 |

> Los modos de falla pueden solaparse en un mismo registro; por eso su suma puede superar el total de fallas.

## 6. Columnas por etapa

### Crudo

`UDI, Product ID, Type, Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Machine failure, TWF, HDF, PWF, OSF, RNF`

### Limpio (HU-04)

`UDI, Product ID, Type, Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Machine failure, TWF, HDF, PWF, OSF, RNF`

### Atípicos analizados (HU-05)

`UDI, Product ID, Type, Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Machine failure, TWF, HDF, PWF, OSF, RNF`

### Transformado (HU-06)

`Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Temp_diff, Type_L, Type_M, Machine failure`

## 7. Cambios de columnas entre etapas

| Etapas | Cambio | Columna | Intencional | Justificación |
| --- | --- | --- | --- | --- |
| Crudo → Limpio (HU-04) | Sin cambios | - | Sí | Esquema conservado |
| Limpio (HU-04) → Atípicos analizados (HU-05) | Sin cambios | - | Sí | Esquema conservado |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Agregada | `Temp_diff` | Sí | Variable derivada `Process temperature - Air temperature` (HU-06, sección 3.5). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Agregada | `Type_L` | Sí | One-Hot Encoding de `Type` (HU-06, sección 3.5). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Agregada | `Type_M` | Sí | One-Hot Encoding de `Type` (HU-06, sección 3.5). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `UDI` | Sí | Identificador no predictivo excluido de las variables de entrada (HU-06). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `Product ID` | Sí | Identificador no predictivo excluido de las variables de entrada (HU-06). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `Type` | Sí | Reemplazada por `Type_L` y `Type_M`; `Type_H` es la categoría de referencia (HU-06). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `TWF` | Sí | Modo de falla excluido para evitar fuga de información (HU-06). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `HDF` | Sí | Modo de falla excluido para evitar fuga de información (HU-06). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `PWF` | Sí | Modo de falla excluido para evitar fuga de información (HU-06). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `OSF` | Sí | Modo de falla excluido para evitar fuga de información (HU-06). |
| Atípicos analizados (HU-05) → Transformado (HU-06) | Eliminada | `RNF` | Sí | Modo de falla excluido para evitar fuga de información (HU-06). |

## 8. Valores representativos (crudo frente a transformado)

El dataset transformado estandariza las variables numéricas; por eso su media es cercana a 0 y su desviación estándar a 1.
`Temp_diff` se calcula sobre el crudo para comparar la variable derivada.

| Variable | Media cruda | Desv. cruda | Mín. / Máx. crudo | Media transformada | Desv. transformada |
| --- | --- | --- | --- | --- | --- |
| `Air temperature [K]` | 300.005 | 2.000 | 295.300 / 304.500 | -0.000 | 1.000 |
| `Process temperature [K]` | 310.006 | 1.484 | 305.700 / 313.800 | 0.000 | 1.000 |
| `Rotational speed [rpm]` | 1538.776 | 179.284 | 1168.000 / 2886.000 | -0.000 | 1.000 |
| `Torque [Nm]` | 39.987 | 9.969 | 3.800 / 76.600 | 0.000 | 1.000 |
| `Tool wear [min]` | 107.951 | 63.654 | 0.000 / 253.000 | 0.000 | 1.000 |
| `Temp_diff` | 10.001 | 1.001 | 7.600 / 12.100 | -0.000 | 1.000 |

## 9. Cambios intencionales por etapa

- Limpieza (HU-04): 0 celdas modificadas y 0 filas eliminadas; no había nulos que imputar.
- Análisis de atípicos (HU-05): 0 celdas modificadas; los atípicos se conservan y solo se documentan.
- Transformación (HU-06): estandarización de variables numéricas, `Temp_diff` derivada, One-Hot de `Type` y exclusión de identificadores y modos de falla.
- La etiqueta `Machine failure` se conserva sin cambios en todas las etapas.
