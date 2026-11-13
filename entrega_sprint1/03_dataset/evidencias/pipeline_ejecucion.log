PredictMain - Ejecucion del pipeline - 2026-11-13 00:07:28 UTC
Directorio de trabajo: entrega_sprint1/03_dataset/ml_service (copia temporal limpia)
Python: Python 3.14.4
$ python -m src.cli ingest --csv ../data/raw/ai4i2020.csv --manifest ../data/raw/manifest.json
============================================================
🚀 PredictMain — HU-01: Ingesta de Datos Crudos
============================================================
Dataset CSV:    ../data/raw/ai4i2020.csv
Manifest JSON:  ../data/raw/manifest.json

✅ Existing manifest verified and preserved. Hash matches.
• Filas de datos:    10,000
• Columnas:          14
• Tamaño archivo:    512,047 bytes
• SHA-256:           59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183
• Inalterado:        True

exit=0
$ python -m src.cli profile --csv ../data/raw/ai4i2020.csv --report ../data/profiling/data-profile-2026-11-11.md
============================================================
📊 PredictMain — HU-02: Perfilado de Telemetría Histórica
============================================================
Dataset CSV:    ../data/raw/ai4i2020.csv
Reporte MD:     ../data/profiling/data-profile-2026-11-11.md

✅ Perfilado estadístico completado correctamente.
• Filas analizadas:  10,000
• Columnas:          14
• Distribución falla: Clase 0: 9,661, Clase 1: 339
• Documento escrito: ../data/profiling/data-profile-2026-11-11.md

exit=0
$ python -m src.cli treat --csv ../data/raw/ai4i2020.csv --output ../data/processed/ai4i2020_clean.csv --report ../reports/null_report.md
============================================================
🧹 PredictMain — HU-04: Tratamiento de Valores Nulos
============================================================
Dataset CSV:    ../data/raw/ai4i2020.csv
Salida limpia:  ../data/processed/ai4i2020_clean.csv
Reporte:        ../reports/null_report.md

✅ Pipeline completado.
• Filas antes:           10,000
• Filas con nulos:       0
• Total nulos:           0
• Filas eliminadas:      0
• Valores imputados:     0
• Filas en salida:       10,000

✅ Verificación post-tratamiento: sin nulos inesperados.

exit=0
$ python -m src.cli outliers --csv ../data/processed/ai4i2020_clean.csv --output ../data/processed/ai4i2020_outlier_analyzed.csv --report ../reports/outlier_report.md
============================================================
📊 PredictMain — HU-05: Análisis de Valores Atípicos
============================================================
Dataset CSV:    ../data/processed/ai4i2020_clean.csv
Salida:         ../data/processed/ai4i2020_outlier_analyzed.csv
Reporte:        ../reports/outlier_report.md

✅ Análisis completado.
• Registros entrada:     10,000
• Outliers detectados:   1,170
• Valores modificados:   0
• Filas excluidas:       0
• Registros salida:      10,000

exit=0
$ python -m src.cli transform --csv ../data/processed/ai4i2020_outlier_analyzed.csv --output ../data/processed/ai4i2020_transformed.csv --pipeline artifacts/pipeline.joblib
============================================================
⚙️  PredictMain — HU-06: Pipeline de Transformación
============================================================
Dataset CSV:    ../data/processed/ai4i2020_outlier_analyzed.csv
Salida CSV:     ../data/processed/ai4i2020_transformed.csv
Pipeline:       artifacts/pipeline.joblib

✅ Pipeline ajustado y guardado.
• Filas transformadas:   10,000
• Columnas de features:  8
• Columnas: ['Air temperature [K]', 'Process temperature [K]', 'Rotational speed [rpm]', 'Torque [Nm]', 'Tool wear [min]', 'Temp_diff', 'Type_L', 'Type_M']
• Pipeline guardado en:  artifacts/pipeline.joblib

exit=0
