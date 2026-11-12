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
