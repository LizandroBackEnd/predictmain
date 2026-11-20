# Inventario de fuentes canónicas y línea base

## Propósito

Este documento fija la línea base utilizada para reconciliar la entrega de Sprint 1
con el proyecto PredictMain. Las rutas bajo `data/` y `ml_service/` son las fuentes
canónicas de procesamiento y no deben modificarse durante la preparación de la
entrega. El PDF original del corpus también es inmutable.

## Fuentes de datos

| Fuente | Tamaño | Filas | Columnas | SHA-256 | Estado |
|---|---:|---:|---:|---|---|
| `data/raw/ai4i2020.csv` | 512,047 bytes | 10,000 | 14 | `59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183` | Canónica |
| `data/processed/ai4i2020_clean.csv` | 513,914 bytes | 10,000 | 14 | `1dcd9c32543beb77921a24c18d79525e698c8b055e85b3320486b427e79f5b1f` | Canónica |
| `data/processed/ai4i2020_outlier_analyzed.csv` | 513,914 bytes | 10,000 | 14 | `1dcd9c32543beb77921a24c18d79525e698c8b055e85b3320486b427e79f5b1f` | Canónica |
| `data/processed/ai4i2020_transformed.csv` | 1,278,232 bytes | 10,000 | 9 | `8cd203892ccb1ff516bb9da64b9b33c39b7241c528a936fbad280009e5e5b833` | Canónica |

El dataset original contiene 339 registros con `Machine failure = 1`, de acuerdo
con el manifiesto y la documentación de la visión.

## Fuente documental original

| Fuente | Tamaño | Páginas | SHA-256 | Metadatos relevantes | Estado |
|---|---:|---:|---|---|---|
| `entrega_sprint1/02_corpus/corpus_original/PredictMain_Corpus_Contenido.pdf` | 236,597 bytes | 26 | `78190c534b822d0245a4e98ff51fc6a77af4d52b7c1c295f105b9b0575b04efe` | Título: `PredictMain_Corpus_Contenido.md`; productor: `Skia/PDF m151`; no cifrado; tamaño A4 | Inmutable |

La documentación existente reporta 18 secciones temáticas, 40,172 caracteres
procesados, 469 párrafos y 11 validaciones de calidad.

## Fuentes canónicas del pipeline

| Fuente | SHA-256 | Uso |
|---|---|---|
| `data/raw/manifest.json` | `1b4359b2ee612f11de9b12dccbb724e6943277fe55d198d7cfb1fe1dc5b6fd0a` | Procedencia, esquema y hash del dataset original |
| `ml_service/requirements.txt` | `fa17e7b5bbbc00daabf2125d41758115bd07e8483728559552c764e1c3202634` | Dependencias reproducibles del pipeline |
| `ml_service/artifacts/pipeline.joblib` | `289fce96140c2b040c6465132563e401f5e9dd97eaf95cfe2da8c60e6c5de680` | Artefacto serializado del pipeline |
| `ml_service/src/` | Código fuente | Ingesta, perfilado, limpieza, análisis de atípicos y transformación |

## Regla de reconciliación

Las copias de `entrega_sprint1/03_dataset/` deben coincidir byte a byte con las
fuentes canónicas cuando representan el mismo artefacto. Los archivos de
documentación y evidencia pueden agregar contexto de entrega, pero no pueden
contradecir filas, columnas, hashes, reglas ni rutas de las fuentes canónicas.

