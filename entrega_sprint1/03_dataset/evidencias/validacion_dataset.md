# Validación del dataset procesado

Generado automáticamente por `scripts_evidencia/validar_dataset_procesado.py`.
El script solo lee los archivos; ante una discrepancia falla y no corrige datos.

## Entradas validadas

- `data/raw/ai4i2020.csv`
- `data/raw/manifest.json`
- `data/processed/ai4i2020_clean.csv`
- `data/processed/ai4i2020_outlier_analyzed.csv`
- `data/processed/ai4i2020_transformed.csv`

## Salidas generadas por el pipeline

- `ml_service/artifacts/pipeline.joblib`
- `reports/null_report.md`
- `reports/outlier_report.md`

## Resultados

| Verificación | Resultado | Detalle |
| --- | --- | --- |
| Dataset crudo con 10.000 filas y 14 columnas | OK | (10000, 14) |
| Esquema canónico del dataset crudo | OK | UDI, Product ID, Type, Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Machine failure, TWF, HDF, PWF, OSF, RNF |
| Dataset limpio conserva 10.000 filas y 14 columnas | OK | (10000, 14) |
| Esquema del dataset limpio igual al crudo | OK | 14 columnas |
| Dataset de atípicos conserva 10.000 filas y 14 columnas | OK | (10000, 14) |
| Esquema del dataset de atípicos igual al crudo | OK | 14 columnas |
| Dataset transformado con 10.000 filas y 9 columnas | OK | (10000, 9) |
| Sin nulos en el dataset crudo | OK | ejecutada: 0 nulos |
| Sin nulos en el dataset limpio | OK | ejecutada: 0 nulos |
| Sin nulos en el dataset de atípicos | OK | ejecutada: 0 nulos |
| Sin nulos en el dataset transformado | OK | ejecutada: 0 nulos |
| Sin duplicados en el dataset crudo | OK | ejecutada: 0 duplicados |
| Sin duplicados en el dataset limpio | OK | ejecutada: 0 duplicados |
| Variable objetivo binaria | OK | valores 0 y 1 |
| Total de fallas igual a 339 | OK | 339 fallas |
| Distribución objetivo esperada en el dataset crudo | OK | {0: 9661, 1: 339} |
| Distribución objetivo esperada en el dataset limpio | OK | {0: 9661, 1: 339} |
| Distribución objetivo esperada en el dataset de atípicos | OK | {0: 9661, 1: 339} |
| Distribución objetivo esperada en el dataset transformado | OK | {0: 9661, 1: 339} |
| Tipos de producto válidos en el dataset crudo | OK | ['H', 'L', 'M'] |
| Tipos de producto válidos en el dataset limpio | OK | ['H', 'L', 'M'] |
| Tipos de producto válidos en el dataset de atípicos | OK | ['H', 'L', 'M'] |
| Distribución de tipos de producto esperada | OK | {'L': 6000, 'M': 2997, 'H': 1003} |
| Codificación one-hot coincide con `Type` | OK | {'Type_L': 6000, 'Type_M': 2997} |
| Modos de falla binarios | OK | TWF, HDF, PWF, OSF, RNF |
| Columnas de entrada del modelo correctas | OK | Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Temp_diff, Type_L, Type_M |
| Etiqueta objetivo al final del dataset transformado | OK | Machine failure |
| Etiqueta objetivo preservada | OK | 339 fallas |
| Manifiesto declara 10.000 filas | OK | 10000 |
| Manifiesto declara 14 columnas | OK | 14 |
| Hash del manifiesto coincide con el CSV | OK | 59db4f1d9c34c581... |
| Hash del CSV coincide con la fuente canónica | OK | 59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183 |
| Manifiesto coincide con la fuente canónica | OK | 59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183 |
| Artefacto del pipeline existe | OK | pipeline.joblib |
| Reporte de nulos existe | OK | null_report.md |
| Reporte de atípicos existe | OK | outlier_report.md |
