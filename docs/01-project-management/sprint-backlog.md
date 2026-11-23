# Sprint Backlog Inicial - PredictMain

> Plan de trabajo y dependencias del Sprint 1 enfocado en la metodología CRISP-DM.

---

## 1. Enfoque del Sprint

El sprint inicial tiene como meta la construcción, entrenamiento, evaluación y empaquetado del modelo predictivo base, así como la infraestructura de trazabilidad de datos sobre el conjunto *AI4I 2020 Predictive Maintenance Dataset*.

---

## 2. Tabla del Product Backlog del Sprint

| ID | Historia de Usuario o Actividad | Descripción Sintética | Prioridad | Dependencia |
| :--- | :--- | :--- | :---: | :---: |
| **HU-01** | Recopilar e ingerir datos crudos | Importar y conservar el dataset original con trazabilidad inalterable en `data/raw/`. | **P0 — Crítica** | *Ninguna* |
| **HU-02** | Estructurar y perfilar la telemetría | Validar esquema, tipos de datos, duplicados, rangos y estadísticas iniciales. | **P0 — Crítica** | HU-01 |
| **HU-03** | Tratar valores faltantes y nulos | Gestionar nulos mediante reglas documentadas, reproducibles y pruebas unitarias. | **P0 — Crítica** | HU-02 |
| **HU-04** | Analizar y gestionar valores atípicos | Evaluar outliers estadísticos sin eliminar señales físicas reales de falla. | **P0 — Crítica** | HU-02 |
| **HU-05** | Construir el pipeline de transformación | Integrar codificación (One-Hot) y variables derivadas en un pipeline reproducible. | **P0 — Crítica** | HU-04 |
| **HU-06** | Validar la matriz de características | Verificar dimensiones, tipos, nulos, variable objetivo y ausencia de fuga (*data leakage*). | **P0 — Crítica** | HU-05 |
| **HU-07** | Preparar los datos y entrenar el modelo base | Dividir los datos (80/20 estratificado) y obtener una primera línea base de clasificación. | **P1 — Alta** | HU-06 |

## 2.1 Trazabilidad de tareas del Taskboard

| Tarea | Historia (Taskboard / código) | Implementación | Evidencia |
| :--- | :--- | :--- | :--- |
| **#30** | HU-05 — Detectar candidatos con IQR 1.5× y percentiles | `ml_service/src/application/outlier_analysis.py`, `ml_service/src/domain/outlier_rules.py` | `reports/outlier_report.md`, `ml_service/notebooks/hu05_outlier_analysis.ipynb` |
| **#31** | HU-05 — Reportar cuántos hay por columna en reports | `ml_service/src/infrastructure/reporting.py` (`build_outlier_report`) | `reports/outlier_report.md` §2 y §5 |
| **#32** | HU-07 — Separar y validar la matriz de características | `ml_service/src/application/matrix_validation.py`, `ml_service/src/interfaces/cli/commands.py` (`run_validate_cmd`) | `data/processed/ai4i2020_features.csv`, `reports/matrix_validation_report.md` |
| **#33** | HU-07 — Revisar calidad de datos y fuga de información | `ml_service/src/application/matrix_validation.py` (checks 3, 4 y 5), `ml_service/src/application/dataset_split.py` | `reports/matrix_validation_report.md` §2 |
| **#34** | HU-07 — Generar reporte final de validación | `ml_service/src/infrastructure/reporting.py` (`build_matrix_validation_report`) | `reports/matrix_validation_report.md` |

> La documentación histórica numera análisis de atípicos, transformación y validación como HU-04, HU-05 y HU-06; el Taskboard y el código usan HU-05, HU-06 y HU-07.

---

## 3. Diagrama de Flujo de Dependencias (CRISP-DM)

```text
[HU-01: Ingesta Cruda]
        │
        ▼
[HU-02: Perfilado & Validación de Esquema]
        │
   ┌────┴─────────────────┐
   ▼                      ▼
[HU-03: Valores Nulos]  [HU-04: Outliers]
                          │
                          ▼
                        [HU-05: Pipeline de Transformación]
                          │
                          ▼
                        [HU-06: Matriz de Características]
                          │
                          ▼
                        [HU-07: Entrenamiento Modelo Base]
```
