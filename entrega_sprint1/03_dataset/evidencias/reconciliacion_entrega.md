# Reconciliación de la entrega con las fuentes canónicas

Generado automáticamente por `scripts_evidencia/reconciliar_entrega.py`.

- Fuente canónica: `data/` y `ml_service/` en la raíz del repositorio (solo lectura).
- Copia de entrega: `entrega_sprint1/03_dataset/data/` y `entrega_sprint1/03_dataset/ml_service/`.

| Verificación | Resultado | Detalle |
| --- | --- | --- |
| Manifiesto: campo `file_name` | OK | coincide |
| Manifiesto: campo `sha256` | OK | coincide |
| Manifiesto: campo `n_rows` | OK | coincide |
| Manifiesto: campo `n_columns` | OK | coincide |
| Manifiesto: campo `columns` | OK | coincide |
| Manifiesto: campo `size_bytes` | OK | coincide |
| Manifiesto canónico describe el CSV canónico | OK | 59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183 |
| CSV crudo de entrega con 10.000 filas y 14 columnas | OK | (10000, 14) |
| Copia `data/raw/ai4i2020.csv` | OK | SHA-256 idéntico |
| Copia `data/processed/ai4i2020_clean.csv` | OK | SHA-256 idéntico |
| Copia `data/processed/ai4i2020_outlier_analyzed.csv` | OK | SHA-256 idéntico |
| Copia `data/processed/ai4i2020_transformed.csv` | OK | SHA-256 idéntico |
| Copia `ml_service/src/__init__.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/application/__init__.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/application/features.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/application/ingestion.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/application/null_treatment.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/application/outlier_analysis.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/application/profiling.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/application/transformation.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/cli.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/domain/__init__.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/domain/models.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/domain/null_rules.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/domain/outlier_rules.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/infrastructure/__init__.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/infrastructure/paths.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/infrastructure/reporting.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/infrastructure/storage.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/interfaces/__init__.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/interfaces/cli/__init__.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/interfaces/cli/commands.py` | OK | SHA-256 idéntico |
| Copia `ml_service/src/interfaces/cli/entrypoint.py` | OK | SHA-256 idéntico |
| Copia `ml_service/requirements.txt` | OK | SHA-256 idéntico |
| Copia `ml_service/artifacts/pipeline.joblib` | OK | SHA-256 idéntico |
| Artefacto `pipeline.joblib` cargable | OK | Pipeline |
