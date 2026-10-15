# Stack Tecnológico y Entorno de Desarrollo - PredictMain

> Especificación de las herramientas, lenguajes, frameworks e infraestructura del proyecto.

---

## 1. Matriz de Tecnologías

| Área | Tecnología Propuesta | Versión / Detalle | Justificación Técnica |
| :--- | :--- | :---: | :--- |
| **Frontend & UI** | **React / Next.js (App Router)** | Next.js 16 | Renderizado híbrido Server Components por defecto para máximo rendimiento. |
| **Lenguaje Frontend** | **TypeScript** | 5.x | Tipado estricto, interfaces compartidas y prevención de errores en compilación. |
| **Diseño & Estilos** | **Tailwind CSS + Shadcn UI** | Latest | Sistema de diseño atómico industrial y componentes accesibles (Radix UI). |
| **Gráficos & Series** | **Recharts** | Latest | Visualización fluida de telemetría y tendencias temporales en tiempo real. |
| **Runtime JS/TS** | **Bun** (`bun`, `bunx`) | 1.x | Ejecución ultrarrápida de scripts, bundling y gestión determinista de paquetes. |
| **Base de Datos** | **PostgreSQL + pgvector** | PostgreSQL 17 | Almacenamiento relacional ACID y motor vectorial nativo para embeddings RAG. |
| **ORM & Modelado** | **Prisma ORM** | Prisma 7 | Consultas fuertemente tipadas y soporte para migraciones automáticas. |
| **Backend ML & API** | **Python + FastAPI** | Python 3.11 | API REST asíncrona de alto rendimiento con validación automática vía Pydantic v2. |
| **Ciencia de Datos** | **Pandas, NumPy, Scikit-learn** | Latest | Pipeline CRISP-DM, manipulación tabular, preprocesamiento y entrenamiento ML. |
| **Entorno Analítico** | **Jupyter Notebooks** | Latest | Análisis exploratorio de datos (EDA) y validación estadística de hipótesis. |
| **Generación Reportes**| **jsPDF / ReportLab** | - | Exportación de bitácoras de servicio y órdenes de trabajo en formato PDF. |
| **RAG & Búsqueda** | **Vercel AI SDK + pgvector** | OpenAI Embeddings | Asistente de consultas técnicas indexado sobre fragmentos de manuales (`document_chunks`). |
| **Control Versiones** | **Git & GitHub** | - | Control distribuido, Conventional Commits y ramas estructuradas. |
| **Contenedores** | **Docker & Docker Compose** | Compose Spec v2 | Despliegue reproducible de la base de datos y aislamiento de servicios. |
| **Calidad & CI/CD** | **GitHub Actions + Pytest + Bun Test** | - | Pruebas unitarias, análisis estático y pipeline de validación continua. |

---

## 2. Aislamiento de Entornos

```text
predictmain/
├── .venv/                   # Entorno virtual de Python aislado para el servicio de ML
├── bun.lock                 # Lockfile determinista para dependencias Node/Next.js
└── docker-compose.yml       # Orquestación local de PostgreSQL 17 con extensión pgvector
```
