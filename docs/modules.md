# Módulos del Sistema - PredictMain

> Descomposición modular bajo principios de Screaming Architecture y Arquitectura Hexagonal (Puertos y Adaptadores).

---

## 1. Visión Modular

La estructura del código fuente comunica de forma inequívoca el propósito del negocio: mantenimiento predictivo industrial. Se evitan divisiones puramente técnicas a nivel raíz y se organizan los componentes en torno a los subdominios del problema.

```text
src/modules/
├── assets-management/       # Subdominio: Catálogo de activos y maquinaria
├── telemetry-ingestion/     # Subdominio: Ingesta y validación de telemetría
├── predictive-analytics/    # Subdominio: Predicción de falla y conexión ML
├── knowledge-base/          # Subdominio: RAG y búsqueda vectorial
└── shared/                  # Núcleo compartido (Prisma, tipos globales)
```

---

## 2. Descripción de Módulos

### 2.1 `assets-management` (Gestión de Activos)
- **Responsabilidad:** Administrar el ciclo de vida de los clientes industriales, plantas, líneas de manufactura y maquinaria registrada.
- **Entidades de Dominio:** `Machine`, `ProductType` (L, M, H), `Customer`, `Plant`.
- **Casos de Uso Principales:**
  - Registrar nueva máquina con sus parámetros nominales.
  - Consultar inventario de máquinas filtrado por estado de salud o criticidad.
  - Actualizar metadatos de activos.

### 2.2 `telemetry-ingestion` (Ingesta de Telemetría)
- **Responsabilidad:** Recepción, validación estructural, control de umbrales y almacenamiento transaccional de mediciones provenientes de los sensores.
- **Entidades de Dominio:** `TelemetryReading`, `ThresholdAlert`.
- **Casos de Uso Principales:**
  - Registrar paquete de telemetría (Air Temp, Process Temp, RPM, Torque, Tool Wear).
  - Evaluar lecturas contra umbrales operativos y emitir alertas inmediatas.
  - Consultar lecturas históricas para alimentación de gráficos de series temporales.

### 2.3 `predictive-analytics` (Analítica Predictiva)
- **Responsabilidad:** Coordinar el cálculo de riesgo de falla interactuando con el motor de inferencia de Machine Learning mediante puertos y adaptadores.
- **Puertos e Interfaces:**
  - `MlPredictionServicePort`: Interfaz abstracta que define el contrato de inferencia (`predictFailureRisk(input: TelemetryFeatures): Promise<PredictionResult>`).
- **Adaptadores:**
  - `FastApiMlAdapter`: Implementación del puerto que consume vía HTTP REST el endpoint `POST /predict` del microservicio en Python.
- **Casos de Uso Principales:**
  - Calcular probabilidad de falla para una máquina específica a partir de su última ventana de telemetría.
  - Almacenar historial de predicciones para auditoría del modelo.

### 2.4 `knowledge-base` (Base de Conocimiento y Asistente RAG)
- **Responsabilidad:** Ingesta de manuales de mantenimiento, segmentación en chunks, generación de embeddings y búsqueda por similitud semántica.
- **Infraestructura:**
  - Almacenamiento vectorial en PostgreSQL 17 utilizando la extensión `pgvector` sobre la tabla `document_chunks`.
  - Índice HNSW para consultas de similitud de cosenos (`<=>`) a alta velocidad.
- **Casos de Uso Principales:**
  - Ingerir y vectorizar manuales técnicos de maquinaria.
  - Buscar fragmentos relevantes para resolver consultas de fallas de los operadores.

### 2.5 `ml_service` (Motor de Machine Learning en Python)
- **Responsabilidad:** Ejecución del pipeline de ciencia de datos bajo metodología CRISP-DM, entrenamiento offline, empaquetado de artefactos (`.pkl`/`.joblib`) y servicio de inferencia en tiempo real vía FastAPI.
- **Estructura Interna:**
  - `data/raw/`: Datos inalterados de telemetría (*AI4I 2020 Predictive Maintenance Dataset*).
  - `data/processed/`: Matrices de características transformadas.
  - `ml_service/artifacts/`: Modelos y transformadores serializados.
  - `ml_service/src/`: Scripts de ingesta, limpieza, ingeniería de variables y entrenamiento.
  - `ml_service/main.py`: Servidor FastAPI exponiendo los endpoints de inferencia.
