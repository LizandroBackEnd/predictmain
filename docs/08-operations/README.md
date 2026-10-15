# 08 - Operaciones (Operations)

> Procedimientos de mantenimiento, monitoreo y respaldo de PredictMain.

- **Respaldos de Datos:** Dump periódico de la base de datos PostgreSQL (`pg_dump`).
- **Mantenimiento de Vectores:** Reindexación periódica de HNSW en pgvector ante cargas masivas de nuevos manuales técnicos.
- **Monitoreo:** Verificación del healthcheck de PostgreSQL (`pg_isready`) y del endpoint `/health` de FastAPI.
