# 🏭 PredictMain

> **Plataforma industrial de mantenimiento predictivo basada en IA, telemetría multivariable y asistencia técnica RAG.**

[![Next.js 16](https://img.shields.io/badge/Next.js-16_App_Router-black?style=flat&logo=next.js)](https://nextjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![Bun](https://img.shields.io/badge/Runtime-Bun-fbf0df?style=flat&logo=bun)](https://bun.sh/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Python_3.11-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17_%2B_pgvector-336791?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![Prisma](https://img.shields.io/badge/ORM-Prisma_7-2D3748?style=flat&logo=prisma)](https://www.prisma.io/)

---

## 1. Visión del Proyecto

**PredictMain** es una plataforma web integral orientada a pequeñas y medianas empresas industriales que dependen de maquinaria crítica para sus operaciones.

La solución transforma datos dispersos de sensores operativos (temperatura ambiental, temperatura del proceso, revoluciones por minuto, torque y desgaste de herramienta) en **indicadores accionables de riesgo de falla mecánica**, permitiendo transicionar de mantenimientos reactivos a un esquema predictivo confiable basado en el *AI4I 2020 Predictive Maintenance Dataset*. Además, incorpora un módulo de **asistencia técnica RAG** (Retrieval-Augmented Generation) sobre manuales técnicos y registros de servicio utilizando búsqueda vectorial nativa.

---

## 2. Metodología: Spec-Driven Development (SDD) & CRISP-DM

El proyecto se rige estrictamente bajo **Spec-Driven Development (SDD)**:

> **Ningún código se escribe sin una especificación técnica validada.** La documentación técnica en [`docs/`](./docs) actúa como la única fuente de verdad (*Single Source of Truth*) para el modelado de datos, interfaces, contratos de API e historias de usuario.

```text
┌───────────────────────────┐      ┌───────────────────────────┐      ┌───────────────────────────┐
│       1. SPECIFY          │  ─►  │       2. CLARIFY          │  ─►  │       3. IMPLEMENT        │
│  Especificación en docs/  │      │  Validación y Contratos   │      │  Next.js Core / ML Engine │
└───────────────────────────┘      └───────────────────────────┘      └───────────────────────────┘
```

- **Ciencia de Datos (CRISP-DM):** El ciclo de vida de los datos sigue las fases de *Business Understanding*, *Data Understanding*, *Data Preparation*, *Modeling*, *Evaluation* y *Deployment*.
- **Software Engineering (Clean Architecture):** Los casos de uso de la aplicación web dependen exclusivamente de abstracciones y puertos (`Ports & Adapters`), manteniendo desacoplado el frontend de las librerías analíticas de Python.

---

## 3. Arquitectura y Stack Tecnológico

El sistema implementa una **arquitectura híbrida desacoplada**:

```text
┌────────────────────────────────────────────────────────┐
│             PredictMain Web Platform                   │
│          (Next.js 16 + Bun + TypeScript)               │
│                                                        │
│  • Web UI & Dashboards (Tailwind CSS + Shadcn UI)      │
│  • Asset & Telemetry CRUD (Prisma 7)                   │
│  • RAG Assistant & Knowledge Base (Vercel AI SDK)      │
│  • Motor de Reportes y Órdenes en PDF                  │
└───────────────────────────┬────────────────────────────┘
                            │
                   HTTP REST│ (FastApiMlAdapter)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Predictive ML Inference Engine             │
│            (Python 3.11 + FastAPI + Sklearn)           │
│                                                        │
│  • Pipeline CRISP-DM de Preprocesamiento               │
│  • Modelo de Riesgo de Falla Serializado (.pkl/.joblib)│
│  • Endpoint de Inferencia POST /predict                │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             Base de Datos y Persistencia               │
│             PostgreSQL 17 + Extensión pgvector         │
│             (Orquestado con Docker Compose)            │
└────────────────────────────────────────────────────────┘
```

### Tecnologías Core

- **Web App & API Principal:**
  - **Framework:** Next.js 16 (App Router, Server Components por defecto).
  - **Lenguaje & Runtime:** TypeScript 5.x ejecutado con **Bun** (`bun`, `bunx`).
  - **Capa de Datos:** Prisma ORM 7 conectado a PostgreSQL 17.
  - **Búsqueda Vectorial:** `pgvector` con indexación HNSW y consultas por distancia de cosenos (`<=>`).
  - **IA & RAG:** Vercel AI SDK con integración de embeddings vectoriales.
  - **Estilos & UI:** Tailwind CSS, Shadcn UI (Radix Primitives) y Recharts para series de tiempo.
- **ML Inference Engine (Python):**
  - **Lenguaje & Framework:** Python 3.11 con **FastAPI** y servidor ASGI **Uvicorn**.
  - **Procesamiento & Modelado:** Pandas, NumPy, Scikit-learn y Joblib para serialización de artefactos (`.pkl`).
- **Contenedores & Orquestación:**
  - Docker & Docker Compose para el entorno de base de datos (`pgvector/pgvector:pg17`).

---

## 4. Estructura de Carpetas (Screaming Architecture & Scope Rule)

El código fuente está organizado siguiendo el principio de **Screaming Architecture** (los directorios reflejan el dominio industrial, no tecnicismos de framework) y la **Scope Rule** (el alcance de uso define la ubicación):

```text
predictmain/
├── docker-compose.yml              # PostgreSQL 17 + pgvector container
├── .env.example                    # Plantilla de variables de entorno
├── prisma/
│   └── schema.prisma               # Modelos de datos: Assets, Telemetry, DocumentChunk
│
├── data/                           # Trazabilidad de datos (CRISP-DM / HU-01)
│   ├── raw/                        # Dataset original AI4I 2020 (Inalterable)
│   └── processed/                  # Matrices transformadas de características
│
├── ml_service/                     # Microservicio de ML e Inferencia
│   ├── .venv/                      # Entorno virtual aislado de Python
│   ├── requirements.txt            # Dependencias: FastAPI, Scikit-learn, Pandas, Uvicorn
│   ├── main.py                     # Servidor FastAPI exponiendo POST /predict
│   ├── artifacts/                  # Modelos y preprocesadores entrenados (.pkl / .joblib)
│   ├── notebooks/                  # EDA y experimentos CRISP-DM
│   └── src/                        # Ingestión, preprocesamiento y entrenamiento
│
├── src/                            # Núcleo de la Plataforma Web (Next.js 16)
│   ├── app/                        # Capa de Entrega (App Router)
│   │   ├── (dashboard)/            # Vistas operativas industriales
│   │   │   ├── assets/             # Catálogo de maquinaria y clientes
│   │   │   ├── telemetry/          # Monitoreo en vivo y gráficos de tendencia
│   │   │   └── predictions/        # Tableros de riesgo y alertas
│   │   ├── api/                    # Endpoints HTTP
│   │   │   ├── chat/route.ts       # Endpoint streaming para Asistente RAG
│   │   │   └── predictions/route.ts# Proxy hacia el microservicio FastAPI
│   │   └── layout.tsx
│   │
│   ├── modules/                    # Núcleo Hexagonal (Casos de Uso y Puertos)
│   │   ├── assets-management/      # Subdominio: Catálogo de activos y maquinaria
│   │   ├── telemetry-ingestion/    # Subdominio: Ingesta y validación de sensores
│   │   ├── predictive-analytics/   # Subdominio: Puertos y FastApiMlAdapter
│   │   ├── knowledge-base/         # Subdominio: Repositorio vectorial y RAG
│   │   └── shared/                 # Kernel compartido (Prisma singleton)
│   │
│   └── components/                 # Componentes UI Compartidos (2+ vistas)
│       ├── ui/                     # Primitivas de Shadcn UI (kebab-case)
│       ├── telemetry/              # Gráficas de sensores con Recharts
│       └── chat/                   # Interfaz de usuario del asistente RAG
│
└── docs/                           # Especificaciones Técnicas y de Negocio (SDD)
    ├── architecture.md             # Visión, principios, Qué ES y Qué NO ES
    ├── roles.md                    # Stakeholders y matriz RACI
    ├── product-capabilities.md     # Catálogo de funcionalidades
    ├── modules.md                  # Detalle de módulos y arquitectura
    └── 01-project-management/ ...  # Backlog, Historias de Usuario (HU-01 a HU-07)
```

---

## 5. Requisitos Previos

Asegúrate de contar con las siguientes herramientas instaladas en tu estación de trabajo:

- **Node.js:** Versión 20.x o superior.
- **Bun:** Runtime y gestor de paquetes (`bun --version` $\ge$ 1.0).
- **Python:** Versión 3.11.x y `pip` / `venv`.
- **Docker & Docker Compose:** Motor de Docker en ejecución.
- **Git:** Control de versiones distribuido.

---

## 6. Guía de Instalación y Levantamiento del Proyecto

Sigue estos 4 pasos secuenciales según tu sistema operativo:

### Paso 1: Clonar el Repositorio y Configurar Variables de Entorno

#### 🐧 Linux / macOS
```bash
git clone https://github.com/LizandroBackEnd/predictmain.git
cd predictmain
cp .env.example .env
```

#### 🪟 Windows (PowerShell)
```powershell
git clone https://github.com/LizandroBackEnd/predictmain.git
cd predictmain
Copy-Item .env.example .env
```

> **Nota:** Verifica que los valores en `.env` coincidan con tus credenciales locales deseadas.

---

### Paso 2: Iniciar la Base de Datos con Docker y Aplicar Migraciones

En la raíz del proyecto:

```bash
# 1. Levantar contenedor de PostgreSQL 17 + pgvector en segundo plano
docker compose up -d

# 2. Generar el cliente de Prisma y aplicar migraciones
bunx prisma generate
bunx prisma migrate dev
```

---

### Paso 3: Configurar y Levantar el Servicio de ML (Python)

Abre una terminal dedicada para el microservicio analítico:

#### 🐧 Linux / macOS
```bash
cd ml_service
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

#### 🪟 Windows (PowerShell)
```powershell
cd ml_service
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

---

### Paso 4: Configurar y Levantar la Aplicación Web (Next.js con Bun)

En una **nueva terminal** en la raíz del proyecto:

```bash
# Instalar dependencias con Bun
bun install

# Iniciar servidor de desarrollo de Next.js
bun dev
```

---

## 7. Endpoints y Puertos por Defecto

| Servicio | URL / Puerto | Descripción |
| :--- | :--- | :--- |
| **Web Application** | `http://localhost:3000` | Dashboard principal de PredictMain (Next.js 16) |
| **ML Inference Service** | `http://localhost:8000` | Microservicio de FastAPI |
| **API Interactive Docs** | `http://localhost:8000/docs` | Documentación interactiva Swagger / OpenAPI de FastAPI |
| **PostgreSQL + pgvector** | `localhost:5432` | Base de datos relacional y vectorial |

---

## 8. Estrategia de Commits (Conventional Commits)

Todos los commits deben seguir rigurosamente la convención estándar **Conventional Commits**:

```text
<type>(<scope>): <summary>

[cuerpo opcional con justificación técnica]
```

### Tipos Permitidos
- `feat`: Nueva funcionalidad.
- `fix`: Corrección de errores.
- `docs`: Modificaciones exclusivas en documentación.
- `style`: Formateo de código sin alterar lógica.
- `refactor`: Refactorización interna de código.
- `test`: Creación o modificación de pruebas unitarias o E2E.
- `chore`: Mantenimiento de herramientas, dependencias o configuración.

### Scopes Autorizados
`assets`, `telemetry`, `predictions`, `rag`, `ml-service`, `prisma`, `ui`, `docs`

**Ejemplos de commits válidos:**
- `feat(predictions): connect Next.js use case with Python FastAPI inference endpoint`
- `fix(telemetry): validate out-of-range sensor values during ingestion`
- `docs(architecture): add what is and what is not section to architecture spec`

---

## 9. Documentación Detallada

Para consultar el análisis a profundidad del dominio y la especificación formal del proyecto, consulta la carpeta [`docs/`](./docs):

- 🏛️ [Arquitectura y Alcance (Qué ES y Qué NO ES)](./docs/architecture.md)
- 👥 [Stakeholders, Roles y Matriz RACI](./docs/roles.md)
- ⚙️ [Capacidades del Producto](./docs/product-capabilities.md)
- 🧩 [Módulos del Sistema (Screaming Architecture)](./docs/modules.md)
- 📋 [Acta de Proyecto y Objetivos](./docs/01-project-management/project-charter.md)
- 📊 [Historias de Usuario (CRISP-DM)](./docs/02-requirements/user-stories.md)
- 🔬 [Comprensión del Dataset AI4I 2020](./docs/03-analysis/data-understanding.md)
