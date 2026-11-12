# Validación del dataset procesado

Generado automáticamente por `scripts_evidencia/validar_dataset_procesado.py`.

| Verificación | Resultado | Detalle |
| --- | --- | --- |
| Dataset crudo con 10.000 filas y 14 columnas | OK | (10000, 14) |
| Dataset limpio conserva 10.000 filas y 14 columnas | OK | (10000, 14) |
| Dataset de atípicos conserva 10.000 filas y 14 columnas | OK | (10000, 14) |
| Dataset transformado con 10.000 filas y 9 columnas | OK | (10000, 9) |
| Sin nulos en el dataset crudo | OK | 0 nulos |
| Sin nulos en el dataset limpio | OK | 0 nulos |
| Sin nulos en el dataset de atípicos | OK | 0 nulos |
| Sin nulos en el dataset transformado | OK | 0 nulos |
| Sin duplicados en el dataset crudo | OK | 0 duplicados |
| Variable objetivo binaria | OK | valores 0 y 1 |
| Total de fallas igual a 339 | OK | 339 fallas |
| Tipos de producto válidos | OK | ['H', 'L', 'M'] |
| Modos de falla binarios | OK | TWF, HDF, PWF, OSF, RNF |
| Columnas de entrada del modelo correctas | OK | Air temperature [K], Process temperature [K], Rotational speed [rpm], Torque [Nm], Tool wear [min], Temp_diff, Type_L, Type_M |
| Etiqueta objetivo al final del dataset transformado | OK | Machine failure |
| Etiqueta objetivo preservada | OK | 339 fallas |
| Manifiesto declara 10.000 filas | OK | 10000 |
| Manifiesto declara 14 columnas | OK | 14 |
| Hash del manifiesto coincide con el CSV | OK | dc6630cd9b1f0f85... |
| Artefacto del pipeline existe | OK | pipeline.joblib |
| Reporte de nulos existe | OK | null_report.md |
| Reporte de atípicos existe | OK | outlier_report.md |
