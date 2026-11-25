# Scripts de la entrega Sprint 2

Todos se ejecutan desde la raíz del repositorio con el PYTHONPATH del servicio ML:

```powershell
$env:PYTHONPATH="ml_service"
python entrega_sprint2/scripts/01_preparar_dataset.py
python entrega_sprint2/scripts/02_analizar_outliers.py
python entrega_sprint2/scripts/03_transformar_validar.py
python entrega_sprint2/scripts/04_entrenar_modelo.py
python entrega_sprint2/scripts/05_evaluar_inferencia.py
python entrega_sprint2/scripts/06_renderizar_pdf.py
```

| Script | Función |
| --- | --- |
| `01_preparar_dataset.py` | Verifica SHA-256, perfila y aplica reglas de nulos (HU-02/03/04). |
| `02_analizar_outliers.py` | Detecta IQR 1.5 + P1/P99 y aplica `KEEP` (HU-05). |
| `03_transformar_validar.py` | Ajusta escalador/codificador solo con entrenamiento y valida la matriz (HU-06/07). |
| `04_entrenar_modelo.py` | Compara regresión logística y Random Forest; guarda el ganador (HU-08). |
| `05_evaluar_inferencia.py` | Ejecuta los 13 casos contra `main.py` y escribe `evidencias/`. |
| `06_renderizar_pdf.py` | Convierte el Markdown en PDF con Chrome headless. |
