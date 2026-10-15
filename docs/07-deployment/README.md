# 07 - Despliegue (Deployment)

> Configuración de ambientes y despliegue de PredictMain.

- **Base de Datos:** Contenedor Docker de PostgreSQL 17 con extensión `pgvector`.
- **Servicio Web:** Contenedor Node/Bun o despliegue en VPS / Vercel.
- **Servicio ML:** Microservicio FastAPI en contenedor Docker o proceso uvicorn independiente.
