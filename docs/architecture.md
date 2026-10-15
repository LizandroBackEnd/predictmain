# Arquitectura del Sistema - PredictMain

> Plataforma web de mantenimiento predictivo basada en inteligencia artificial para pequeñas y medianas empresas industriales.

---

## 1. Visión General

**PredictMain** es una solución integral diseñada para modernizar la gestión del mantenimiento en plantas industriales mediante la centralización de variables operativas, análisis de telemetría y algoritmos de Machine Learning.

Su propósito central es transformar datos operativos dispersos en **información accionable**, permitiendo anticipar fallas mecánicas, reducir paros no programados y optimizar la vida útil de los equipos críticos.

---

## 2. Definición de Alcance: Qué ES y Qué NO ES el Proyecto

Para asegurar la viabilidad técnica y el foco estratégico del producto, el alcance del sistema se delimita de forma estricta:

### Lo que ES PredictMain (Alcance Inicial)

- **Plataforma Web Centralizada:** Registro y administración de catálogo de clientes, líneas de producción, tipos de producto y maquinaria.
- **Ingesta de Telemetría Operativa:** Captura estructurada de variables físicas clave: temperatura del aire, temperatura del proceso, velocidad de rotación (RPM), torque y desgaste de herramienta (tool wear).
- **Modelo Predictivo de Falla:** Estimación probabilística de riesgo de falla y detección de patrones anómalos basada en el dataset industrial *AI4I 2020 Predictive Maintenance Dataset*.
- **Monitoreo y Visualización:** Tableros interactivos con series temporales, detección de tendencias y umbrales críticos de operación.
- **Gestión de Alertas:** Generación automática de eventos preventivos basados en condiciones operativas y umbrales configurables.
- **Documentación Operativa:** Generación automatizada de bitácoras de servicio y órdenes de trabajo en formato PDF.
- **Asistente Técnico RAG:** Base de conocimiento indexada mediante embeddings vectoriales (`pgvector`) para consulta contextual de manuales y registros de mantenimiento.

### Lo que NO ES PredictMain (Fuera del Alcance Inicial)

- **NO es un sistema SCADA o PLC en tiempo real:** No realiza control supervisorio industrial ni interacción directa con buses de campo o protocolos propietarios en planta en esta primera versión.
- **NO es un actuador físico:** El sistema genera alertas e información para la toma de decisiones; bajo ninguna circunstancia acciona switches, relevadores o paros automáticos de emergencia sobre la maquinaria física.
- **NO sustituye el criterio técnico:** La plataforma es una herramienta de apoyo para los ingenieros de mantenimiento y jefes de planta, no un reemplazo de la inspección experta humana.
- **NO es un ERP ni CMMS general:** No administra inventarios globales de repuestos, contabilidad, nóminas, compras ni facturación empresarial.
- **NO es una aplicación móvil nativa:** La solución se concibe como una Progressive Web App (PWA) / Web App responsiva accesible desde cualquier navegador moderno.
- **NO garantiza infalibilidad:** Los modelos de Machine Learning estiman probabilidades de riesgo; no constituyen una garantía matemática absoluta de cero fallas operativas.
- **NO es una plataforma multi-tenant comercial:** No incluye en esta etapa pasarelas de pago, esquemas de suscripción SaaS ni facturación multiempresa.

---

## 3. Principios de Diseño Arquitectónico

El sistema sigue tres principios fundamentales para mantener desacoplamiento, mantenibilidad y escalabilidad:

### Principio 1: Separación Híbrida Estricta (Web Core vs. ML Service)

```text
┌────────────────────────────────────────────────────────┐
│             PredictMain Web Platform                   │
│          (Next.js 16 + Bun + TypeScript)               │
│                                                        │
│  • Web UI & Dashboards (Tailwind + Shadcn)             │
│  • Asset & Telemetry CRUD (Prisma 7)                   │
│  • RAG Assistant & Knowledge Base (pgvector)           │
│  • PDF Export Engine                                   │
└───────────────────────────┬────────────────────────────┘
                            │
                   HTTP REST│ (FastApiMlAdapter)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Predictive ML Inference Engine             │
│            (Python 3.11 + FastAPI + Sklearn)           │
│                                                        │
│  • CRISP-DM Data Pipelines                             │
│  • Data Profiling & Feature Preprocessing              │
│  • Machine Failure Risk Model (.pkl / joblib)          │
└────────────────────────────────────────────────────────┘
```

- El entorno **Next.js** gestiona presentación, ingesta transaccional y orquestación. Nunca ejecuta scripts de Python directamente.
- El servicio **FastAPI** opera como motor analítico puro, stateless e independiente.

### Principio 2: Screaming Architecture

La estructura de carpetas y módulos del proyecto refleja directamente el dominio de mantenimiento predictivo industrial:

- `assets-management/`: Modelado de plantas, líneas, máquinas y tipos de producto (L, M, H).
- `telemetry-ingestion/`: Ingesta, validación y almacenamiento de lecturas de sensores.
- `predictive-analytics/`: Cálculo de riesgo de falla y cliente HTTP hacia el motor ML.
- `knowledge-base/`: Búsqueda semántica de manuales técnicos mediante similitud de cosenos (`<=>`).

### Principio 3: Scope Rule ("El alcance determina la estructura")

- Componentes o utilidades utilizados por **dos o más características** pertenecen a módulos compartidos (`src/modules/` o `src/components/ui/`).
- Componentes utilizados por **una sola vista** residen exclusivamente de manera local en el subdirectorio de dicha ruta (ej. `_components/`).

---

## 4. Mapa de Navegación Documental

| Documento | Descripción |
| :--- | :--- |
| [roles.md](file:///home/lizdev/Escritorio/projects/predictmain/docs/roles.md) | Stakeholders, usuarios objetivo y responsabilidades del proyecto. |
| [product-capabilities.md](file:///home/lizdev/Escritorio/projects/predictmain/docs/product-capabilities.md) | Capacidades funcionales detalladas y catálogo de funciones. |
| [modules.md](file:///home/lizdev/Escritorio/projects/predictmain/docs/modules.md) | Módulos del dominio, puertos y adaptadores del sistema. |
| [01-project-management/](file:///home/lizdev/Escritorio/projects/predictmain/docs/01-project-management) | Carta del proyecto, objetivos y Sprint Backlog inicial. |
| [02-requirements/](file:///home/lizdev/Escritorio/projects/predictmain/docs/02-requirements) | Historias de usuario, requerimientos funcionales (RF) y no funcionales (RNF). |
| [03-analysis/](file:///home/lizdev/Escritorio/projects/predictmain/docs/03-analysis) | Comprensión y análisis exploratorio del dataset industrial AI4I 2020. |
| [04-design/](file:///home/lizdev/Escritorio/projects/predictmain/docs/04-design) | Stack tecnológico, arquitectura de software y diagramas de diseño. |
