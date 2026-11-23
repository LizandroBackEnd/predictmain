# 05 - Desarrollo (Development)

> Directrices técnicas, arquitectura y guías operativas para el desarrollo en PredictMain.

---

## 1. Principios y Reglas de Desarrollo

- **Separación Híbrida Estricta:**
  - Next.js 16 + Bun administra la UI, la ingesta vía API, reportes y el asistente RAG.
  - Python 3.11 (`ml_service/`) administra el pipeline analítico CRISP-DM y la inferencia vía FastAPI.
  - Next.js jamás ejecuta código Python directamente; se comunica exclusivamente vía HTTP REST (`FastApiMlAdapter`).
- **Regla de Alcance (Scope Rule):**
  - Componentes o utilitarios usados en 1 sola vista o ruta se mantienen locales (e.g. `_components/`).
  - Código reutilizado en 2 o más vistas va a `src/components/` o `src/modules/`.
- **Estrategia de Commits:** Conventional Commits obligatorios (`feat`, `fix`, `docs`, `refactor`, `test`, etc.).
- **Runtime & Gestor:** Utilizar estrictamente `bun` y `bunx` en frontend; nunca `npm` ni `npx`.

---

## 2. Documentos y Guías del Módulo

| Documento | Descripción | Cobertura |
| :--- | :--- | :---: |
| [Pipeline de Datos y Modelo Base](./data-pipeline.md) | CLI, Clean Architecture, anti-fuga, entrenamiento HU-08 y pruebas | **HU-02** … **HU-08** |

---

## 3. Comandos Rápidos de Desarrollo

### Frontend (Next.js con Bun)
```bash
bun install
bun dev
```

### ML Service (Python en `ml_service/`)
```bash
cd ml_service
source .venv/bin/activate
pip install -r requirements.txt

# Pipeline de datos y modelo base
python -m src.cli ingest     # HU-02
python -m src.cli profile    # HU-03
python -m src.cli treat      # HU-04
python -m src.cli outliers   # HU-05
python -m src.cli transform  # HU-06
python -m src.cli validate   # HU-07
python -m src.cli train      # HU-08 → artifacts/modelo.joblib + reports/model_baseline.md
python -m src.cli all        # hasta validate (sin train)

# Pruebas unitarias
python -m unittest discover -s tests
```
