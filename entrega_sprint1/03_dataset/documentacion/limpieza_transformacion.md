# Limpieza y transformación del dataset

> Documentación del pipeline CRISP-DM aplicado al AI4I 2020 Predictive Maintenance Dataset.

## 1. Fuente y trazabilidad

| Elemento | Valor |
| :--- | :--- |
| Dataset | AI4I 2020 Predictive Maintenance Dataset |
| Origen | UCI Machine Learning Repository |
| Archivo crudo | `data/raw/ai4i2020.csv` |
| Registros | 10,000 |
| Columnas | 14 |
| Tamaño | 512,047 bytes |
| SHA-256 | `59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183` |
| Manifiesto | `data/raw/manifest.json` |
| Codificación | UTF-8 |
| Separador | coma |

### 1.1 Reconciliación con la fuente canónica

La fuente de verdad del dataset y del pipeline está en `data/` y `ml_service/` en la raíz del repositorio. La carpeta `03_dataset/` es una copia de entrega sincronizada byte a byte con esas fuentes.

Una versión anterior de esta entrega contenía el CSV con finales de línea CRLF (`dc6630cd...`, 522,048 bytes) y un manifiesto regenerado para ese archivo. Esa copia se reemplazó por el CSV canónico con finales de línea LF y su manifiesto original (`59db4f1d...`, 512,047 bytes).

Ambos archivos tienen el mismo contenido: convertir los 10,001 finales de línea del CSV canónico a CRLF produce exactamente el SHA-256 `dc6630cd...`, que es el valor que el corpus (sección 17.3) registra para la copia auditada del ZIP oficial de UCI. La diferencia de 10,001 bytes corresponde a un carácter `\r` por línea.

`scripts_evidencia/reconciliar_entrega.py` compara el manifiesto campo por campo, el SHA-256 de cada CSV, el código fuente, `requirements.txt` y `pipeline.joblib` con la fuente canónica, y verifica que el artefacto se pueda cargar. Si alguna copia está desactualizada, el script falla e indica la ruta afectada sin modificar ningún archivo.

Evidencia: `evidencias/reconciliacion_entrega.md`.

## 2. Estructura del pipeline

```text
03_dataset/ml_service/
├── src/
│   ├── application/
│   │   ├── ingestion.py          # HU-01: validación e integridad
│   │   ├── profiling.py          # HU-02: perfilado estadístico
│   │   ├── null_treatment.py     # HU-04: tratamiento de nulos
│   │   ├── outlier_analysis.py   # HU-05: análisis de atípicos
│   │   ├── transformation.py     # HU-06: escalado y codificación
│   │   └── features.py           # Definición de variables
│   ├── domain/
│   │   ├── models.py             # Entidades del dominio
│   │   ├── null_rules.py         # Reglas de tratamiento de nulos
│   │   └── outlier_rules.py      # Reglas de atípicos
│   ├── infrastructure/
│   │   ├── paths.py              # Resolución de rutas
│   │   ├── reporting.py          # Generación de reportes Markdown
│   │   └── storage.py            # Persistencia de artefactos
│   └── interfaces/cli/           # Comandos de línea de comandos
└── artifacts/pipeline.joblib     # Pipeline de preprocesamiento serializado
```

## 3. Etapas del pipeline

### 3.1 Ingesta (HU-01)

- Lee el CSV crudo.
- Calcula SHA-256.
- Genera o verifica `manifest.json`.
- Si el hash no coincide con un manifiesto existente, aborta sin sobrescribir.
- No modifica el archivo crudo.

### 3.2 Perfilado (HU-02)

Genera `data/profiling/data-profile-2026-11-11.md` con:

- Resumen dimensional.
- Estadísticas de variables numéricas.
- Distribución de `Type`.
- Distribución de `Machine failure` y modos de falla.
- Control de calidad contra la ficha técnica UCI.

Resultados principales:

| Métrica | Valor |
| :--- | :--- |
| Registros | 10,000 |
| Columnas | 14 |
| Nulos | 0 |
| Duplicados | 0 |
| Fallas | 339 (3.39%) |
| Tipo L / M / H | 6,000 / 2,997 / 1,003 |

### 3.3 Tratamiento de nulos (HU-04)

El dataset no contenía nulos, por lo que no se imputó ni eliminó ningún registro. Aun así, las reglas quedan definidas y documentadas:

| Columna | Decisión | Estrategia |
| :--- | :--- | :--- |
| `UDI` | KEEP | Identificador; nunca se imputa |
| `Product ID` | KEEP | Identificador compuesto; nunca se imputa |
| `Type` | IMPUTE | Moda |
| `Air temperature [K]` | IMPUTE | Mediana |
| `Process temperature [K]` | IMPUTE | Mediana |
| `Rotational speed [rpm]` | IMPUTE | Mediana |
| `Torque [Nm]` | IMPUTE | Mediana |
| `Tool wear [min]` | IMPUTE | Mediana |
| `Machine failure` | DROP_ROW | Etiqueta objetivo; si falta, la fila no es entrenable |
| `TWF`, `HDF`, `PWF`, `OSF`, `RNF` | DROP_ROW | Etiquetas de modo de falla; misma razón |

Resultado:

| Métrica | Valor |
| :--- | :--- |
| Filas antes | 10,000 |
| Filas con nulos | 0 |
| Nulos totales | 0 |
| Filas eliminadas | 0 |
| Valores imputados | 0 |
| Filas después | 10,000 |

Evidencia: `reports/null_report.md`.

#### 3.3.1 Duplicados

El dataset no contiene filas duplicadas exactas. Se verificó la combinación de todas las columnas y también el identificador `UDI`. No se eliminó ningún registro.

| Verificación | Resultado |
| :--- | :--- |
| Filas duplicadas exactas | 0 |
| `UDI` duplicados | 0 |
| Filas eliminadas por duplicidad | 0 |

La decisión es conservar todos los registros porque cada `UDI` representa una observación distinta y no se detectaron copias exactas.

#### 3.3.2 Inconsistencias entre etiqueta y modos

Se identificaron 27 registros con relaciones inconsistentes entre `Machine failure` y los modos de falla:

| Situación | Registros | Decisión |
| :--- | :--- | :--- |
| `Machine failure = 0` con al menos un modo activo | 18 | Conservar y respetar la etiqueta original. |
| `Machine failure = 1` sin ningún modo activo | 9 | Conservar y respetar la etiqueta original. |

No se reetiquetaron ni eliminaron registros. La justificación completa está en `04_etiquetado/reglas_etiquetado.md` y la validación en `04_etiquetado/validacion_etiquetado.md`.

### 3.4 Análisis de atípicos (HU-05)

Se aplicaron dos métodos por variable:

1. Cerca IQR con factor 1.5.
2. Percentiles P1 y P99.

Ningún atípico se eliminó ni se recortó. Todos los valores se conservaron porque representan condiciones físicas válidas o precursores de falla.

| Variable | Tipo | Decisión | Detectados |
| :--- | :--- | :--- | :--- |
| `Air temperature [K]` | valid_extreme | KEEP | 162 |
| `Process temperature [K]` | valid_extreme | KEEP | 195 |
| `Rotational speed [rpm]` | failure_signal | KEEP | 516 |
| `Torque [Nm]` | failure_signal | KEEP | 198 |
| `Tool wear [min]` | valid_extreme | KEEP | 99 |

Resultado: 1,170 valores atípicos detectados, 0 modificados, 0 filas excluidas, 10,000 registros de salida.

Evidencia: `reports/outlier_report.md`.

### 3.5 Transformación (HU-06)

Variables de entrada finales:

| Variable | Tratamiento | Justificación |
| :--- | :--- | :--- |
| `Air temperature [K]` | Estandarización | Las variables tienen escalas muy distintas (K, rpm, Nm, min); `StandardScaler` evita que las de mayor magnitud dominen el modelo. |
| `Process temperature [K]` | Estandarización | Misma razón. |
| `Rotational speed [rpm]` | Estandarización | Misma razón; los atípicos se conservan porque la estandarización no los recorta. |
| `Torque [Nm]` | Estandarización | Misma razón. |
| `Tool wear [min]` | Estandarización | Misma razón. |
| `Temp_diff` | Variable derivada: `Process temperature - Air temperature`; estandarización | La diferencia térmica es el indicador físico de la falla por disipación de calor (HDF). |
| `Type_L` | One-Hot Encoding | `Type` es categórica nominal (L, M, H); la codificación evita imponer un orden numérico. |
| `Type_M` | One-Hot Encoding | Misma razón. |

`Type_H` se elimina como categoría de referencia (`drop='first'`) para evitar columnas colineales.

Variables categóricas validadas:

| Variable | Categorías esperadas | Distribución |
| :--- | :--- | :--- |
| `Type` | L, M, H | 6,000 / 2,997 / 1,003 |
| `Type_L`, `Type_M` | 0, 1 | 6,000 y 2,997 registros con valor 1, consistentes con `Type` |

Variables excluidas:

- `UDI` y `Product ID`: identificadores, no predictivos.
- `TWF`, `HDF`, `PWF`, `OSF`, `RNF`: etiquetas auxiliares; se excluyen para evitar fuga de información.

Resultado:

| Métrica | Valor |
| :--- | :--- |
| Filas transformadas | 10,000 |
| Variables de entrada | 8 |
| Variable objetivo | `Machine failure` |
| Columnas de salida | 9 (8 variables + objetivo) |

Evidencia: `data/processed/ai4i2020_transformed.csv` y `ml_service/artifacts/pipeline.joblib`.

### 3.6 Etiqueta objetivo

| Elemento | Decisión | Justificación |
| :--- | :--- | :--- |
| `Machine failure` | Se conserva sin modificar como variable objetivo binaria | Es la etiqueta original de UCI; reetiquetar introduciría un sesgo no verificable. |
| Distribución | 9,661 registros sin falla (96.61%) y 339 con falla (3.39%) | El desbalance se documenta y se trata en la estrategia de entrenamiento, no alterando los datos. |
| Modos `TWF`, `HDF`, `PWF`, `OSF`, `RNF` | Se conservan en los datasets limpio y de atípicos, y se excluyen del transformado | Describen la causa de la falla y producirían fuga de información si se usaran como entrada. |
| Inconsistencias etiqueta-modo | 27 registros conservados con su etiqueta original | Ver sección 3.3.2. |

La validación comprueba que la distribución de la etiqueta sea idéntica en las cuatro etapas.

## 4. Comparativa de datasets

| Etapa | Archivo | Filas | Columnas | Nulos | Fallas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Crudo | `ai4i2020.csv` | 10,000 | 14 | 0 | 339 |
| Limpio | `ai4i2020_clean.csv` | 10,000 | 14 | 0 | 339 |
| Atípicos analizados | `ai4i2020_outlier_analyzed.csv` | 10,000 | 14 | 0 | 339 |
| Transformado | `ai4i2020_transformed.csv` | 10,000 | 9 | 0 | 339 |

Evidencia completa: `evidencias/comparativa_datasets.md`. Además de las dimensiones, la comparativa reporta las columnas agregadas o eliminadas por etapa (todas intencionales), las celdas modificadas en limpieza y análisis de atípicos (0 en ambas) y valores representativos del dataset crudo frente al transformado.

## 5. Validación

`scripts_evidencia/validar_dataset_procesado.py` ejecuta 36 verificaciones sobre esquema, filas, nulos, duplicados, categorías de `Type`, distribución de la etiqueta en cada etapa, codificación one-hot, manifiesto y artefactos. Todas pasaron. Un hallazgo de cero registros se informa como verificación ejecutada con conteo 0, no como verificación omitida.

Si falta una entrada, el script falla indicando la ruta y no genera el reporte. Si un archivo no coincide con lo esperado, la verificación correspondiente aparece como `FALLA` y el script termina con código 1 sin corregir el archivo.

Evidencia: `evidencias/validacion_dataset.md` y `evidencias/validacion_dataset.log`.

## 6. Reproducibilidad

Entorno: Python 3.11 o superior con las dependencias de `ml_service/requirements.txt`.

Desde `03_dataset/ml_service/`:

```bash
python -m src.cli ingest --csv ../data/raw/ai4i2020.csv --manifest ../data/raw/manifest.json
python -m src.cli profile --csv ../data/raw/ai4i2020.csv --report ../data/profiling/data-profile-2026-11-11.md
python -m src.cli treat --csv ../data/raw/ai4i2020.csv --output ../data/processed/ai4i2020_clean.csv --report ../reports/null_report.md
python -m src.cli outliers --csv ../data/processed/ai4i2020_clean.csv --output ../data/processed/ai4i2020_outlier_analyzed.csv --report ../reports/outlier_report.md
python -m src.cli transform --csv ../data/processed/ai4i2020_outlier_analyzed.csv --output ../data/processed/ai4i2020_transformed.csv --pipeline artifacts/pipeline.joblib
```

> Las rutas deben indicarse explícitamente. Sin argumentos, el CLI resuelve la raíz del repositorio y escribiría sobre `data/` y `ml_service/` canónicos.

La última ejecución se realizó en una copia temporal limpia de `03_dataset/`. Los CSV procesados, el manifiesto y `pipeline.joblib` resultantes fueron idénticos byte a byte a los de la entrega; los reportes solo difieren en la fecha de generación.

Después, desde la raíz del repositorio:

```bash
python entrega_sprint1/03_dataset/scripts_evidencia/reconciliar_entrega.py
python entrega_sprint1/03_dataset/scripts_evidencia/comparar_datasets.py
python entrega_sprint1/03_dataset/scripts_evidencia/validar_dataset_procesado.py
```

Logs: `evidencias/pipeline_ejecucion.log` y `evidencias/validacion_dataset.log`.

## 7. Copias del código

Las copias de `03_dataset/ml_service/` son idénticas a `ml_service/` canónico, incluidos comentarios y docstrings. La reconciliación lo verifica por SHA-256 archivo por archivo.
