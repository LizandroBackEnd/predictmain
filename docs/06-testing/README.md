# 06 - Pruebas y Calidad (Testing)

> Estrategia de pruebas unitarias, de integración y validación de modelos en PredictMain.

---

## 1. Pruebas del Servicio de Machine Learning (`ml_service/`)

Las pruebas unitarias del pipeline analítico residen en `ml_service/tests/` y validan la integridad de datos, cálculo de hash criptográfico, idempotencia de manifiestos y cálculo de estadísticas descriptivas.

### Ejecución de Pruebas:

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

### Módulos de Prueba Actuales:
- `tests/test_ingestion.py` (5 tests):
  - Validación de dimensionalidad del archivo crudo (10,000 registros × 14 columnas).
  - Cálculo determinista de hash SHA-256.
  - Creación de `data/raw/manifest.json`.
  - Idempotencia del manifiesto ante ejecuciones repetidas.
  - Detección y rechazo de violaciones de integridad por alteración de datos.
- `tests/test_profiling.py` (2 tests):
  - Cálculo de métricas estadísticas (mín, máx, media, mediana, desviación estándar).
  - Generación del reporte en formato Markdown compatible con GitHub.

---

## 2. Pruebas de la Aplicación Web (Frontend / Next.js)

- **Framework:** Bun Test / Vitest.
- **Alcance:** Pruebas unitarias de casos de uso en `src/modules/*/use-cases/` y renderizado de componentes compartidos.

```bash
bun test
```

---

## 3. Validación de Modelos de ML

- **Fase:** Modelado predictivo (CRISP-DM Fase 4 & 5).
- **Métricas Clave:** PR-AUC, F1-Score, Recall sobre clase minoritaria (`Machine failure = 1`), y Matrices de Confusión evaluadas bajo validación cruzada estratificada (`StratifiedKFold`).

