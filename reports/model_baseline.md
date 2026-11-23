# Reporte de Modelo Base — HU-08

> Generado automáticamente por el pipeline de entrenamiento de PredictMain.

---

## 1. Resumen de la ejecución

| Métrica | Valor |
| :--- | :--- |
| Archivo fuente | `ai4i2020_outlier_analyzed.csv` |
| Fecha de ejecución | 2026-11-23 01:04:20 UTC |
| División | 75% / 25% estratificada |
| `random_state` | 42 |
| Filas de entrenamiento | 7,500 |
| Filas de prueba | 2,500 |
| Estratificación | Sí |
| Modelo seleccionado | `random_forest` |
| Artefacto | `/home/lizdev/Escritorio/projects/predictmain/ml_service/artifacts/modelo.joblib` |

Selección: mayor F1; en empate, mayor recall; si persiste el empate, `random_forest`.

---

## 2. Comparativa de métricas (conjunto de prueba)

| Modelo | Accuracy | Precision | Recall | F1 | ROC-AUC |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `logistic_regression` | 0.8256 | 0.1411 | 0.8118 | 0.2404 | 0.8836 |
| `random_forest` | 0.9848 | 0.7901 | 0.7529 | 0.7711 | 0.9703 |

---

## 3. Conclusión

El modelo serializado en `/home/lizdev/Escritorio/projects/predictmain/ml_service/artifacts/modelo.joblib` es `random_forest`. El preprocesador HU-06 se ajustó solo con el conjunto de entrenamiento antes de evaluar el test.

---

> **Reporte generado:** 2026-11-23 01:04:20 UTC
