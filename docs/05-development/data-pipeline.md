# Pipeline de Datos y Modelo Base (Clean Architecture)

> Guía técnica de ejecución, arquitectura y testing del pipeline CRISP-DM en `ml_service/` (**HU-02** a **HU-08**).

---

## 1. Visión y Arquitectura

El pipeline vive en `ml_service/src/` bajo Clean Architecture. La CLI (`python -m src.cli <comando>`) solo enruta; la lógica está en `application/`, las reglas en `domain/` y la I/O en `infrastructure/`.

```text
ml_service/src/
├── domain/
│   ├── models.py              # Resultados inmutables (manifiesto, métricas, baseline, …)
│   ├── null_rules.py          # Reglas de nulos (HU-04)
│   └── outlier_rules.py       # Reglas de atípicos (HU-05)
├── application/
│   ├── ingestion.py           # HU-02
│   ├── profiling.py           # HU-03
│   ├── null_treatment.py      # HU-04
│   ├── outlier_analysis.py    # HU-05
│   ├── transformation.py      # HU-06
│   ├── dataset_split.py       # Partición reproducible (default 80/20; HU-08 usa 75/25)
│   ├── matrix_validation.py   # HU-07
│   ├── baseline_training.py   # HU-08
│   └── features.py            # Definición de columnas y Temp_diff
├── infrastructure/
│   ├── paths.py               # Raíz del workspace y rutas por defecto
│   ├── storage.py             # joblib: pipeline.joblib y modelo.joblib
│   └── reporting.py           # Reportes Markdown en reports/
└── interfaces/cli/
    ├── entrypoint.py          # argparse y subcomandos
    └── commands.py            # Handlers delgados
```

---

## 2. Comandos CLI

Desde `ml_service/` con el entorno virtual activo:

```bash
cd ml_service
source .venv/bin/activate

python -m src.cli ingest      # HU-02 → data/raw/manifest.json
python -m src.cli profile     # HU-03 → data/profiling/data-profile-YYYY-MM-DD.md
python -m src.cli treat       # HU-04 → data/processed/ai4i2020_clean.csv + reports/null_report.md
python -m src.cli outliers    # HU-05 → data/processed/ai4i2020_outlier_analyzed.csv + reports/outlier_report.md
python -m src.cli transform   # HU-06 → data/processed/ai4i2020_transformed.csv + artifacts/pipeline.joblib
python -m src.cli validate    # HU-07 → data/processed/ai4i2020_features.csv + reports/matrix_validation_report.md
python -m src.cli train       # HU-08 → artifacts/modelo.joblib + reports/model_baseline.md
python -m src.cli all         # ingest → profile → treat → outliers → transform → validate
```

Desde la raíz del repositorio:

```bash
PYTHONPATH=ml_service ./ml_service/.venv/bin/python -m src.cli train \
  --csv data/processed/ai4i2020_outlier_analyzed.csv \
  --model ml_service/artifacts/modelo.joblib \
  --report reports/model_baseline.md
```

> **Importante:** sin argumentos de ruta, `paths.py` resuelve la raíz del repo (marcadores `.git` / `package.json` / `docker-compose.yml`) y escribe en `data/`, `reports/` y `ml_service/artifacts/` canónicos.

---

## 3. Detalle por Historia

### HU-02 — `ingest`
- **Entrada:** `data/raw/ai4i2020.csv` (10,000 × 14, inmutable).
- **Salida:** `data/raw/manifest.json` con SHA-256, filas, columnas y metadatos.
- **Comportamiento:** crea el manifiesto si no existe; si el hash coincide, no lo altera; si difiere, aborta sin sobrescribir.

### HU-03 — `profile`
- **Entrada:** CSV crudo.
- **Salida:** `data/profiling/data-profile-YYYY-MM-DD.md` (dimensiones, sensores, `Type`, fallas y modos).

### HU-04 — `treat`
- **Entrada:** CSV crudo.
- **Salida:** `data/processed/ai4i2020_clean.csv`, `reports/null_report.md`.
- **Reglas:** imputación vectorizada / drop de filas con etiqueta nula según `null_rules.py`.

### HU-05 — `outliers`
- **Entrada:** dataset limpio.
- **Salida:** `data/processed/ai4i2020_outlier_analyzed.csv`, `reports/outlier_report.md`.
- **Política:** detectar (IQR / percentiles); conservar señales físicas de falla (KEEP).

### HU-06 — `transform`
- **Entrada:** dataset de atípicos (o el CSV indicado).
- **Salida:** `data/processed/ai4i2020_transformed.csv`, `artifacts/pipeline.joblib`, `reports/transformation_report.md`.
- **Contrato:** `Temp_diff`, `StandardScaler`, One-Hot de `Type` (`drop='first'`). El ajuste del scaler/encoder se hace solo sobre la partición de entrenamiento del flujo HU-06 (default `test_size=0.20`) para evitar fuga.

### HU-07 — `validate`
- **Entrada:** matriz transformada.
- **Salida:** `data/processed/ai4i2020_features.csv` (X sin `y`), `reports/matrix_validation_report.md`.
- **Checks:** dimensiones, tipos, nulos, objetivo y ausencia de columnas de fuga.

### HU-08 — `train`
- **Entrada por defecto:** `data/processed/ai4i2020_outlier_analyzed.csv`.
- **Salidas:**
  - `ml_service/artifacts/modelo.joblib` — `Pipeline` compuesto (`preprocess` HU-06 + clasificador seleccionado).
  - `reports/model_baseline.md` — tabla comparativa Accuracy / Precision / Recall / F1 / ROC-AUC.
- **Contrato de división:** 75 % train / 25 % test, `random_state=42`, estratificado sobre `Machine failure` cuando es posible. Se pasa `test_size=0.25` de forma explícita; el default compartido de `split_dataset` sigue en **0.20** para no romper HU-06.
- **Modelos:** Logistic Regression (`class_weight=balanced`, `max_iter=1000`) y Random Forest (`class_weight=balanced`, `n_estimators=300`, `random_state=42`).
- **Selección:** mayor F1; empate → mayor recall; empate total → `random_forest`.
- **Anti-fuga:** el preprocesador HU-06 se reajusta solo con el 75 % de entrenamiento de HU-08; el test solo se transforma. No se sobrescribe `artifacts/pipeline.joblib` de HU-06.

Resultado de referencia de la ejecución documentada:

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
| :--- | ---: | ---: | ---: | ---: | ---: |
| logistic_regression | 0.8256 | 0.1411 | 0.8118 | 0.2404 | 0.8836 |
| **random_forest** (seleccionado) | 0.9848 | 0.7901 | 0.7529 | 0.7711 | 0.9703 |

Evidencia: [`reports/model_baseline.md`](../../reports/model_baseline.md).

---

## 4. Flujo de Datos (HU-08)

```text
ai4i2020_outlier_analyzed.csv
        │
        ▼
split_dataset(test_size=0.25, random_state=42, stratify)
        │
        ├── train ──► TransformationService.fit_transform
        │                      │
        │                      ▼
        └── test ──► transform (sin refit)
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        LogisticRegression            RandomForestClassifier
                 │                           │
                 └──── métricas en test ─────┘
                               │
                    seleccionar por F1 / recall
                               │
              ┌────────────────┴────────────────┐
              ▼                                 ▼
     artifacts/modelo.joblib          reports/model_baseline.md
```

---

## 5. Pruebas

```bash
cd ml_service
python -m unittest discover -s tests

# Enfoque HU-08 + regresión del split HU-06:
python -m unittest tests.test_baseline_training tests.test_cli_train tests.test_dataset_split -v
```

Cobertura relevante de HU-08:
- `tests/test_baseline_training.py` — 75/25 reproducible, fallback sin estratificar, anti-fuga del scaler, selección F1/recall, artefacto y reporte.
- `tests/test_cli_train.py` — `train` exit 0 con artefactos; exit 1 si falta el CSV (sin escribir `modelo.joblib`).
- `tests/test_dataset_split.py` — default 80/20 de HU-06 intacto.

---

## 6. Relación con la entrega Sprint 1

La carpeta `entrega_sprint1/` es una proyección de entrega. La fuente canónica del pipeline y del modelo base es `data/` + `ml_service/`. La configuración y el estado de HU-08 en la entrega viven en `entrega_sprint1/05_entrenamiento/` (por ejemplo `config_entrenamiento.json` con `status: executed`).
