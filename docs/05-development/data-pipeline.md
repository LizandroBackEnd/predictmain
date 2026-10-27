# Pipeline de Datos y Telemetría (Clean Architecture)

> Guía técnica de ejecución, arquitectura y testing del pipeline de ingesta y perfilado de datos para PredictMain (**HU-01** y **HU-02**).

---

## 1. Visión y Arquitectura

El pipeline de datos reemplaza los scripts procedimentales monolíticos preliminares por una arquitectura desacoplada en `ml_service/src/`:

```text
ml_service/src/
├── domain/               # Entidades y value objects inmutables
│   └── models.py         # ManifestData, ValidationResult, DatasetSummary, ColumnMetric
│
├── ingestion/            # Caso de Uso: Ingesta e integridad (HU-01)
│   └── service.py        # Validación estructural, cálculo SHA-256 e idempotencia
│
├── profiling/            # Caso de Uso: Perfilado estadístico (HU-02)
│   ├── service.py        # Métricas, cardinalidad y distribución de clases
│   └── report_builder.py # Generador del reporte técnico Markdown
│
├── infrastructure/       # Adaptadores de infraestructura
│   └── paths.py          # Resolución dinámica de la raíz del workspace
│
└── cli.py                # Fachada CLI unificada (entrypoint del pipeline)
```

---

## 2. Equivalencia con Scripts Preliminares (Proyecto Legacy)

En la versión preliminar del proyecto (`PredictMain` anterior / refactor), el proceso dependía de scripts procedimentales sueltos ejecutados en la raíz sin arquitectura modular. En la arquitectura actual de PredictMain, estos scripts fueron refactorizados e integrados bajo Clean Architecture:

| Funcionalidad | Script Anterior (Legacy) | Comando Actual Unificado (Clean Architecture) | Historia de Usuario |
| :--- | :--- | :--- | :---: |
| **Ingesta y Manifiesto** | `python scripts/create_manifest.py` | `python -m src.cli ingest` | **HU-01** |
| **Perfilado Estadístico** | `python scripts/profile_data.py` | `python -m src.cli profile` | **HU-02** |
| **Ejecución Completa** | *(No existía — requería 2 pasos manuales)* | `python -m src.cli all` | **HU-01 + HU-02** |

---

## 3. Guía de Ejecución desde la Terminal

Puedes ejecutar el pipeline de datos mediante cualquiera de las siguientes dos opciones:

### Opción A: Desde la carpeta `ml_service/` (Recomendado)

```bash
# 1. Ingresar al directorio del microservicio
cd ml_service

# 2. Activar el entorno virtual
source .venv/bin/activate       # En Linux / macOS
# .\.venv\Scripts\Activate.ps1  # En Windows (PowerShell)

# 3. Ejecutar los comandos individuales o integrales:
python -m src.cli ingest   # Paso 1: Valida dataset y genera/verifica data/raw/manifest.json
python -m src.cli profile  # Paso 2: Calcula estadísticas y genera docs/03-analysis/data-profile.md
python -m src.cli all      # Paso 1 + 2: Ejecuta ambos procesos secuencialmente
```

### Opción B: Directamente desde la Raíz del Proyecto (`predictmain/`)

Si estás trabajando en la raíz y no deseas cambiar de directorio:

#### 🐧 Linux / macOS:
```bash
PYTHONPATH=ml_service ./ml_service/.venv/bin/python -m src.cli ingest
PYTHONPATH=ml_service ./ml_service/.venv/bin/python -m src.cli profile
PYTHONPATH=ml_service ./ml_service/.venv/bin/python -m src.cli all
```

#### 🪟 Windows (PowerShell):
```powershell
$env:PYTHONPATH="ml_service"; .\ml_service\.venv\Scripts\python.exe -m src.cli ingest
$env:PYTHONPATH="ml_service"; .\ml_service\.venv\Scripts\python.exe -m src.cli profile
$env:PYTHONPATH="ml_service"; .\ml_service\.venv\Scripts\python.exe -m src.cli all
```

---

## 4. Detalle de Salidas y Comportamiento

### Comando: `python -m src.cli ingest` (HU-01)
- **Entrada:** `data/raw/ai4i2020.csv` (10,000 registros, 14 columnas, permisos de solo lectura `chmod 444`).
- **Salida:** `data/raw/manifest.json`.
- **Garantía de Idempotencia:**
  1. Computa el hash SHA-256 sobre el stream de bytes crudos (`59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183`).
  2. Si `manifest.json` no existe, lo crea con metadatos de integridad y fecha ISO.
  3. Si `manifest.json` ya existe y el hash coincide exactamente, preserva el manifiesto existente (`Existing manifest verified and preserved. Hash matches.`).
  4. Si el archivo CSV fue modificado o corrupto, aborta inmediatamente con excepción de violación de integridad sin sobrescribir.

### Comando: `python -m src.cli profile` (HU-02)
- **Entrada:** `data/raw/ai4i2020.csv`.
- **Salida:** `docs/03-analysis/data-profile.md`.
- **Métricas computadas:**
  1. Resumen dimensional (10,000 filas × 14 columnas).
  2. Estadísticas de variables continuas de telemetría: mín, máx, media, mediana, desviación estándar y cardinalidad para:
     - `Air temperature [K]`
     - `Process temperature [K]`
     - `Rotational speed [rpm]`
     - `Torque [Nm]`
     - `Tool wear [min]`
  3. Distribución de variantes de producto `Type`: L (60%), M (29.97%), H (10.03%).
  4. Distribución de la variable objetivo `Machine failure` (339 fallas = 3.39%) y de los 5 modos mecánicos:
     - `TWF` (Tool Wear Failure): 46
     - `HDF` (Heat Dissipation Failure): 115
     - `PWF` (Power Failure): 95
     - `OSF` (Overstrain Failure): 98
     - `RNF` (Random Failure): 19
  5. Checklist de conformidad frente a la ficha técnica oficial de la UCI.

---

## 5. Salida Típica en Terminal (`python -m src.cli all`)

```text
============================================================
PREDICTMAIN DATA INGESTION & PROFILING PIPELINE
============================================================
[INFO] Project Root resolved at: /home/.../predictmain
[INFO] Starting ingestion verification for data/raw/ai4i2020.csv...
[INFO] Existing manifest verified and preserved. Hash matches: 59db4f1d9c34c58136d89e5a006ec190dcea19e9dbea74f6b3b0c6f22a44d183
[SUCCESS] Ingestion completed. Manifest is valid at data/raw/manifest.json
[INFO] Starting telemetry dataset profiling...
[INFO] Profiling complete. 10000 rows and 14 columns analyzed.
[SUCCESS] Data profile report generated at docs/03-analysis/data-profile.md
============================================================
PIPELINE COMPLETED SUCCESSFULLY
============================================================
```

---

## 6. Pruebas Unitarias Automatizadas

La lógica de negocio está protegida con pruebas unitarias en `ml_service/tests/`:

### Ejecución de Pruebas:
```bash
# Desde ml_service/ con el entorno virtual activo:
python -m unittest discover -s tests

# O desde la raíz del proyecto:
PYTHONPATH=ml_service ./ml_service/.venv/bin/python -m unittest discover -s ml_service/tests
```

### Cobertura de las Pruebas:
- `test_ingestion.py` (5 pruebas):
  - `test_csv_inspection`: Valida las 10,000 filas y 14 columnas exactas.
  - `test_sha256_computation`: Valida cálculo determinista de hash criptográfico.
  - `test_manifest_creation`: Valida creación de `manifest.json` cuando no existe.
  - `test_manifest_idempotency`: Valida que si el hash coincide, el archivo no se sobreescribe innecesariamente.
  - `test_manifest_integrity_mismatch`: Valida que si el hash cambia, se rechaza la operación por fallo de integridad.
- `test_profiling.py` (2 pruebas):
  - `test_profiling_calculations`: Valida que las métricas numéricas y distribuciones categóricas coincidan con los datos.
  - `test_report_builder_markdown`: Valida que el documento Markdown generado contenga todas las secciones requeridas.

Resultado de la suite:
```text
.......
----------------------------------------------------------------------
Ran 7 tests in 0.028s

OK
```

