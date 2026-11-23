# 06 - Pruebas y Calidad (Testing)

> Estrategia de pruebas unitarias, de integración y validación de modelos en PredictMain.

---

## 1. Pruebas del Servicio de Machine Learning (`ml_service/`)

Las pruebas unitarias del pipeline analítico residen en `ml_service/tests/` y cubren integridad de datos, hash criptográfico, preparación, transformación, validación de matriz y entrenamiento de línea base (HU-08).

### Ejecución de Pruebas

#### Opción A: Desde `ml_service/` (con `.venv` activo)
```bash
cd ml_service
source .venv/bin/activate
python -m unittest discover -s tests
```

#### Opción B: Desde la Raíz del Proyecto (`predictmain/`)
```bash
PYTHONPATH=ml_service ./ml_service/.venv/bin/python -m unittest discover -s ml_service/tests
```

### Módulos de Prueba Relevantes

| Módulo | Foco |
| :--- | :--- |
| `tests/test_ingestion.py` | Dimensiones del CSV, SHA-256, creación/idempotencia/integridad del manifiesto |
| `tests/test_profiling.py` | Métricas descriptivas y reporte Markdown |
| `tests/test_null_treatment.py` | Reglas de nulos e imputación |
| `tests/test_outlier_analysis.py` | Detección de atípicos y política KEEP |
| `tests/test_transformation.py` / `tests/test_cli_transformation.py` | Pipeline HU-06, anti-fuga del scaler |
| `tests/test_dataset_split.py` | Default 80/20 de HU-06, estratificación y reproducibilidad |
| `tests/test_matrix_validation.py` | Checks de la matriz final (HU-07) |
| `tests/test_baseline_training.py` | Split 75/25 de HU-08, anti-fuga, selección F1/recall, artefacto y reporte |
| `tests/test_cli_train.py` | CLI `train`: exit 0 con artefactos; exit 1 sin CSV |

Enfoque rápido de HU-08 + regresión del split:

```bash
cd ml_service
python -m unittest tests.test_baseline_training tests.test_cli_train tests.test_dataset_split -v
```

---

## 2. Pruebas de la Aplicación Web (Frontend / Next.js)

- **Framework:** Bun Test / Vitest.
- **Alcance:** Pruebas unitarias de casos de uso en `src/modules/*/use-cases/` y renderizado de componentes compartidos.

```bash
bun test
```

---

## 3. Validación de Modelos de ML

- **Fase actual (HU-08):** línea base supervisada con partición 75/25 estratificada (`random_state=42`).
- **Modelos comparados:** Logistic Regression y Random Forest (`class_weight=balanced`).
- **Métricas en test:** Accuracy, Precision, Recall, F1 y ROC-AUC (ver `reports/model_baseline.md`).
- **Selección:** mayor F1; empate → recall; empate total → `random_forest`.
- **Artefacto:** `ml_service/artifacts/modelo.joblib` (preprocess HU-06 + clasificador seleccionado).
- **Diferido:** búsqueda de hiperparámetros, optimización de umbral y `StratifiedKFold` completo (documentado en `entrega_sprint1/05_entrenamiento/`).
