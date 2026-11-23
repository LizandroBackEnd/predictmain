# Sprint Backlog Inicial - PredictMain

> Plan de trabajo y dependencias del Sprint 1 enfocado en la metodología CRISP-DM.

---

## 1. Enfoque del Sprint

El sprint inicial construye el corpus documental, la infraestructura de trazabilidad de datos, la preparación de características y la línea base predictiva del dataset *AI4I 2020 Predictive Maintenance Dataset*.

---

## 2. Tabla del Product Backlog del Sprint

| ID | Historia de Usuario o Actividad | Descripción Sintética | Prioridad | Dependencia |
| :--- | :--- | :--- | :---: | :---: |
| **HU-01** | Construir el corpus documental | Extraer, limpiar y validar el PDF técnico canónico para el asistente RAG. | **Alta** | *Ninguna* |
| **HU-02** | Recopilar e ingerir datos crudos | Importar y conservar el dataset original con trazabilidad inalterable en `data/raw/`. | **Crítica** | *Ninguna* |
| **HU-03** | Estructurar y perfilar la telemetría | Validar esquema, tipos de datos, duplicados, rangos y estadísticas iniciales. | **Crítica** | HU-02 |
| **HU-04** | Tratar valores faltantes y nulos | Gestionar nulos mediante reglas documentadas, reproducibles y pruebas unitarias. | **Crítica** | HU-03 |
| **HU-05** | Analizar y gestionar valores atípicos | Evaluar outliers estadísticos sin eliminar señales físicas reales de falla. | **Crítica** | HU-03 |
| **HU-06** | Construir el pipeline de transformación | Integrar codificación (One-Hot) y variables derivadas en un pipeline reproducible. | **Crítica** | HU-05 |
| **HU-07** | Validar la matriz de características | Verificar dimensiones, tipos, nulos, variable objetivo y ausencia de fuga (*data leakage*). | **Crítica** | HU-06 |
| **HU-08** | Preparar los datos y entrenar el modelo base | Dividir 75/25 estratificado, entrenar la línea base y registrar sus métricas. | **Alta** | HU-07 |

> **Nota:** la división correcta de HU-08 es **75 % entrenamiento / 25 % prueba**, según el Taskboard. La referencia 80/20 de la versión histórica quedó superada.

## 2.1 Trazabilidad de tareas del Taskboard

| Tarea | Historia (Taskboard / código) | Implementación | Evidencia |
| :--- | :--- | :--- | :--- |
| **#30** | HU-05 — Detectar candidatos con IQR 1.5× y percentiles | `ml_service/src/application/outlier_analysis.py`, `ml_service/src/domain/outlier_rules.py` | `reports/outlier_report.md`, `ml_service/notebooks/hu05_outlier_analysis.ipynb` |
| **#31** | HU-05 — Reportar cuántos hay por columna en reports | `ml_service/src/infrastructure/reporting.py` (`build_outlier_report`) | `reports/outlier_report.md` §2 y §5 |
| **#32** | HU-07 — Separar y validar la matriz de características | `ml_service/src/application/matrix_validation.py`, `ml_service/src/interfaces/cli/commands.py` (`run_validate_cmd`) | `data/processed/ai4i2020_features.csv`, `reports/matrix_validation_report.md` |
| **#33** | HU-07 — Revisar calidad de datos y fuga de información | `ml_service/src/application/matrix_validation.py` (checks 3, 4 y 5), `ml_service/src/application/dataset_split.py` | `reports/matrix_validation_report.md` §2 |
| **#34** | HU-07 — Generar reporte final de validación | `ml_service/src/infrastructure/reporting.py` (`build_matrix_validation_report`) | `reports/matrix_validation_report.md` |
| **#35** | HU-08 — División estratégica y preparación del dataset | `ml_service/src/application/dataset_split.py` | `reports/model_baseline.md` §2 |
| **#36** | HU-08 — Entrenamiento de modelos base y serialización | `ml_service/src/application/` (por implementar) | `ml_service/artifacts/modelo.joblib` |
| **#37** | HU-08 — Evaluación de métricas y generación del reporte final | `ml_service/src/infrastructure/reporting.py` (por implementar) | `reports/model_baseline.md` |

> **Convención oficial:** HU-01 corpus; HU-02 ingesta; HU-03 perfilado; HU-04 nulos; HU-05 outliers; HU-06 transformación; HU-07 matriz; HU-08 entrenamiento. La documentación histórica usó un desfase de una posición: ingesta HU-01, perfilado HU-02, nulos HU-03, outliers HU-04, transformación HU-05, matriz HU-06 y entrenamiento HU-07.

---

## 3. Diagrama de Flujo de Dependencias (CRISP-DM)

```text
[HU-01: Corpus Documental] ─────────────┐
                                        │ (evidencia para el asistente RAG)
[HU-02: Ingesta Cruda]                  │
        │                               │
        ▼                               │
[HU-03: Perfilado & Validación]         │
   ┌────┴──────────────┐                │
   ▼                   ▼                │
[HU-04: Nulos]   [HU-05: Outliers]      │
                   │                    │
                   ▼                    │
        [HU-06: Pipeline de Transformación]
                   │
                   ▼
        [HU-07: Matriz de Características]
                   │
                   ▼
        [HU-08: Entrenamiento Modelo Base]
```
