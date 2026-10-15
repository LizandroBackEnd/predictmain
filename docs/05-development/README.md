# 05 - Desarrollo (Development)

> Directrices y guías para el desarrollo del proyecto PredictMain.

- **Stack Local:** Bun para frontend Next.js, Python 3.11 con venv para ML Service, Docker Compose para PostgreSQL + pgvector.
- **Convención de Commits:** Conventional Commits (`feat(...)`, `fix(...)`, `docs(...)`, etc.).
- **Regla de Alcance:** Componentes usados en 1 vista se mantienen en `_components/`; usados en 2+ van a `src/components/` o `src/modules/`.
