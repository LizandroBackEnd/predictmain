# Requerimientos Funcionales - PredictMain

> Catálogo de Requerimientos Funcionales (RF-01 a RF-14) para la fase inicial del proyecto.

---

## 1. Matriz de Requerimientos Funcionales

| ID | Requerimiento Funcional | Historia Relacionada | Prioridad |
| :--- | :--- | :---: | :---: |
| **RF-01** | Importar automáticamente el dataset desde la fuente oficial o repositorio autorizado. | HU-01 | **P0 — Crítica** |
| **RF-02** | Almacenar los datos originales en `data/raw/` sin aplicar modificaciones ni transformaciones. | HU-01 | **P0 — Crítica** |
| **RF-03** | Generar un manifiesto de ingesta con origen, versión, fecha, tamaño, filas y columnas. | HU-01 | **P0 — Crítica** |
| **RF-04** | Validar y documentar el esquema, tipos de datos, duplicados, rangos, cardinalidad y estadísticas iniciales. | HU-02 | **P0 — Crítica** |
| **RF-05** | Identificar y cuantificar los valores faltantes antes de aplicar cualquier tratamiento. | HU-03 | **P0 — Crítica** |
| **RF-06** | Aplicar un tratamiento documentado y reproducible para los valores faltantes. | HU-03 | **P0 — Crítica** |
| **RF-07** | Detectar y analizar valores atípicos mediante reglas estadísticas o límites operativos justificados. | HU-04 | **P0 — Crítica** |
| **RF-08** | Permitir documentar si los valores atípicos se conservan, transforman o excluyen. | HU-04 | **P0 — Crítica** |
| **RF-09** | Codificar variables categóricas y generar variables derivadas dentro de un pipeline automatizado. | HU-05 | **P0 — Crítica** |
| **RF-10** | Aplicar las transformaciones de forma consistente a los datos de entrenamiento, prueba y nuevos datos. | HU-05 | **P0 — Crítica** |
| **RF-11** | Validar la matriz final de características, la variable objetivo, los tipos de datos y la ausencia de fuga de información. | HU-06 | **P0 — Crítica** |
| **RF-12** | Dividir el dataset en entrenamiento y prueba, preferentemente con estratificación cuando exista desbalance. | HU-07 | **P1 — Alta** |
| **RF-13** | Entrenar un modelo base de clasificación utilizando el pipeline de transformación. | HU-07 | **P1 — Alta** |
| **RF-14** | Generar predicciones iniciales y registrar el resultado del entrenamiento para su evaluación posterior. | HU-07 | **P1 — Alta** |
