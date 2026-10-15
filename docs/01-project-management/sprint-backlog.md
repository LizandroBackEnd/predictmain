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
