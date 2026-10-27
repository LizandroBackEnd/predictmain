# Historias de Usuario - PredictMain

> Especificación de Historias de Usuario (HU-01 a HU-07) bajo metodología CRISP-DM.

---

## HU-01: Recopilar e Ingerir Datos Crudos

- **Rol:** Como ingeniero de datos
- **Acción:** Quiero automatizar la descarga, carga e ingesta del dataset histórico en una estructura controlada
- **Beneficio:** Para asegurar que el equipo trabaje sobre una fuente base inalterable, trazable y versionada.
- **Prioridad:** **P0 — Crítica**

### Criterios de Aceptación
1. Existe un script o proceso automatizado en Python que importa los datos desde la fuente oficial o repositorio autorizado.
2. Los datos originales se almacenan en `data/raw/` sin modificaciones, limpieza ni transformaciones previas.
3. Se genera un manifiesto con fecha de ingesta, origen, nombre y versión del archivo, número de filas, columnas y tamaño.
4. Se registra un checksum o hash del archivo cuando el tamaño y el entorno lo permitan.
5. El proceso es idempotente: una ejecución repetida no duplica ni altera la fuente original.
6. El código y la configuración de ingesta están versionados en el repositorio Git.

> **Implementación Técnica:**
> - Comando: `python -m src.cli ingest` (servicio `ml_service/src/ingestion/service.py`).
> - Artefacto generado: [`data/raw/manifest.json`](../../data/raw/manifest.json) con SHA-256 (`59db4f1d...`).
> - Pruebas: `ml_service/tests/test_ingestion.py` (5 tests de hash, esquema e idempotencia).
> - Guía: [`docs/05-development/data-pipeline.md`](../05-development/data-pipeline.md).

---

## HU-02: Estructurar Tipos de Datos y Perfilar la Telemetría Histórica

- **Rol:** Como científico de datos
- **Acción:** Quiero analizar y documentar los tipos de datos, el esquema y los metadatos de la telemetría
- **Beneficio:** Para conocer la calidad y consistencia técnica de las variables antes de transformarlas.
- **Prioridad:** **P0 — Crítica**

### Criterios de Aceptación
1. Se documentan los tipos de datos numéricos, categóricos, booleanos y de identificación de cada columna.
2. Se identifican registros duplicados, columnas inconsistentes, valores imposibles y problemas de estructura.
3. Se genera un reporte inicial con rangos, conteos, cardinalidad, estadísticas descriptivas y distribución de la variable objetivo.
4. Se documentan las variables candidatas para el modelado y sus posibles limitaciones.
5. El script de validación de esquema y el reporte de perfilado quedan versionados.

> **Implementación Técnica:**
> - Comando: `python -m src.cli profile` (servicio `ml_service/src/profiling/service.py`).
> - Artefacto generado: [`docs/03-analysis/data-profile.md`](../03-analysis/data-profile.md).
> - Pruebas: `ml_service/tests/test_profiling.py` (2 tests de métricas y builder).
> - Guía: [`docs/05-development/data-pipeline.md`](../05-development/data-pipeline.md).

---

## HU-03: Tratar Valores Faltantes y Nulos

- **Rol:** Como científico de datos
- **Acción:** Quiero identificar y gestionar los valores faltantes de la telemetría
- **Beneficio:** Para evitar errores de ejecución y sesgos durante el entrenamiento.
- **Prioridad:** **P0 — Crítica**

### Criterios de Aceptación
1. Se cuantifican los valores faltantes por columna y por registro antes de aplicar cualquier tratamiento.
2. Cada decisión de eliminación, imputación o conservación tiene una justificación técnica documentada.
3. El pipeline de tratamiento está automatizado y es reproducible utilizando Python, Pandas y NumPy.
4. El dataset final no contiene valores nulos inesperados en las variables requeridas por el modelo.
5. Se ejecutan pruebas unitarias que validan la salida del proceso.
6. Se registra cuántos valores fueron imputados, eliminados o conservados.

---

## HU-04: Analizar y Gestionar Valores Atípicos

- **Rol:** Como científico de datos
- **Acción:** Quiero analizar los valores atípicos de los sensores
- **Beneficio:** Para decidir justificadamente si se conservan, transforman o excluyen sin alterar la realidad física de la maquinaria.
- **Prioridad:** **P0 — Crítica**

### Criterios de Aceptación
1. Los valores atípicos no se eliminan automáticamente.
2. Se aplican reglas documentadas, como rango intercuartílico (IQR), percentiles o límites operativos de ingeniería.
3. Se distingue entre error de medición, valor extremo válido y posible señal de falla real.
4. Se documenta la regla aplicada para conservar, transformar o excluir cada grupo de outliers.
5. El proceso genera un resumen cuantitativo de registros detectados, modificados y excluidos.
6. La decisión final puede ser revisada en el notebook o reporte técnico.

---

## HU-05: Construir el Pipeline de Transformación

- **Rol:** Como científico de datos
- **Acción:** Quiero integrar las transformaciones de las variables en un pipeline automatizado
- **Beneficio:** Para aplicar el mismo procesamiento durante el entrenamiento y la predicción.
- **Prioridad:** **P0 — Crítica**

### Criterios de Aceptación
1. Las variables categóricas se codifican mediante One-Hot Encoding u otra técnica justificada.
2. Se generan variables derivadas relevantes, como la diferencia entre temperatura del aire y temperatura del proceso.
3. Las transformaciones se ajustan (*fit*) únicamente con el conjunto de entrenamiento.
4. El pipeline puede transformar datos de prueba sin errores (*transform*).
5. El pipeline puede guardarse y cargarse nuevamente en formato serializado.
6. El código queda versionado en el repositorio.

---

## HU-06: Validar la Matriz de Características

- **Rol:** Como científico de datos
- **Acción:** Quiero validar la matriz final de características y la variable objetivo
- **Beneficio:** Para asegurar que los datos estén preparados correctamente antes del entrenamiento.
- **Prioridad:** **P0 — Crítica**

### Criterios de Aceptación
1. La matriz final contiene las variables documentadas.
2. La variable objetivo se encuentra separada de las variables predictoras.
3. No existen valores nulos inesperados en la matriz final.
4. Las variables tienen tipos de datos compatibles con el modelo de aprendizaje.
5. Se verifica formalmente que no exista fuga de información (*data leakage*).
6. El pipeline puede aplicarse de la misma forma a datos nuevos en producción.
7. Se genera un reporte con las dimensiones y características finales.

---

## HU-07: Preparar los Datos y Entrenar el Modelo Base

- **Rol:** Como científico de datos
- **Acción:** Quiero dividir los datos y entrenar un modelo base de clasificación
- **Beneficio:** Para establecer una primera línea de predicción del riesgo de falla.
- **Prioridad:** **P1 — Alta**

### Criterios de Aceptación
1. El dataset se divide en 80 % para entrenamiento y 20 % para prueba.
2. La división es estratificada cuando existe desbalance entre las clases de falla.
3. Se define una semilla aleatoria fija (*random_state*) para reproducir la división.
4. Se entrena al menos un modelo base de clasificación.
5. El modelo utiliza el pipeline de transformación definido en la HU-05.
6. El código se ejecuta de principio a fin sin errores en el entorno configurado.
7. Se generan predicciones iniciales sobre el conjunto de prueba para su evaluación métrica.
