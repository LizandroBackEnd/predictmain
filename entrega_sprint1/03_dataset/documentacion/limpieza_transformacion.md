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
| Tamaño | 522,048 bytes |
| SHA-256 | `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e` |
| Manifiesto | `data/raw/manifest.json` |
| Codificación | UTF-8 |
| Separador | coma |

### 1.1 Nota sobre el manifiesto

El repositorio original incluía un manifiesto con un hash distinto (`59db4f1d...`) al del CSV efectivamente incluido. Al ejecutar la ingesta, el servicio detectó la discrepancia y se negó a sobrescribir el manifiesto para proteger la integridad.

Para esta entrega se regeneró un manifiesto consistente con el archivo incluido. El nuevo hash es `dc6630cd9b1f0f853922fad78a1b6436570d3f1ec863f1dd5c4340ac56bc8a8e`. La discrepancia se documenta en `evidencias/validacion_dataset.md`; el manifiesto obsoleto no forma parte de la entrega.

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

| Variable | Tratamiento |
| :--- | :--- |
| `Air temperature [K]` | Estandarización |
| `Process temperature [K]` | Estandarización |
| `Rotational speed [rpm]` | Estandarización |
| `Torque [Nm]` | Estandarización |
| `Tool wear [min]` | Estandarización |
| `Temp_diff` | Variable derivada: `Process temperature - Air temperature`; estandarización |
| `Type_L` | One-Hot Encoding |
| `Type_M` | One-Hot Encoding |

`Type_H` se elimina como categoría de referencia (`drop='first'`).

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

## 4. Comparativa de datasets

| Etapa | Archivo | Filas | Columnas | Nulos | Fallas |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Crudo | `ai4i2020.csv` | 10,000 | 14 | 0 | 339 |
| Limpio | `ai4i2020_clean.csv` | 10,000 | 14 | 0 | 339 |
| Atípicos analizados | `ai4i2020_outlier_analyzed.csv` | 10,000 | 14 | 0 | 339 |
| Transformado | `ai4i2020_transformed.csv` | 10,000 | 9 | 0 | 339 |

Evidencia completa: `evidencias/comparativa_datasets.md`.

## 5. Validación

Se ejecutaron 22 verificaciones automáticas sobre dimensiones, nulos, etiquetas, columnas, manifiesto y artefactos. Todas pasaron.

Evidencia: `evidencias/validacion_dataset.md`.

## 6. Reproducibilidad

Desde `03_dataset/ml_service/`:

```powershell
python -m src.cli ingest --csv ..\data\raw\ai4i2020.csv --manifest ..\data\raw\manifest.json
python -m src.cli profile --csv ..\data\raw\ai4i2020.csv --report ..\data\profiling\data-profile-2026-11-11.md
python -m src.cli treat --csv ..\data\raw\ai4i2020.csv --output ..\data\processed\ai4i2020_clean.csv --report ..\reports\null_report.md
python -m src.cli outliers --csv ..\data\processed\ai4i2020_clean.csv --output ..\data\processed\ai4i2020_outlier_analyzed.csv --report ..\reports\outlier_report.md
python -m src.cli transform --csv ..\data\processed\ai4i2020_outlier_analyzed.csv --output ..\data\processed\ai4i2020_transformed.csv --pipeline artifacts\pipeline.joblib
```

Log completo: `evidencias/pipeline_ejecucion.log`.

## 7. Nota sobre traducción

Las copias de los scripts en `03_dataset/ml_service/` conservan el código original. **Solo se tradujeron los comentarios `#` al español.** Los docstrings, strings, justificaciones de reportes y nombres de variables permanecen en su idioma original.
