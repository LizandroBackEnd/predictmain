# 03 - Análisis y Comprensión de Datos (Data Understanding)

> Documentación de la fase de análisis exploratorio, catálogo de variables y perfilado estadístico del dataset AI4I 2020 Predictive Maintenance Dataset (**CRISP-DM Fase 2**).

---

## 1. Documentos Disponibles

| Documento | Descripción | Tipo |
| :--- | :--- | :---: |
| [Comprensión del Dataset (Data Understanding)](./data-understanding.md) | Origen del dataset, diccionario de variables, modos mecánicos de falla y consideraciones de ingeniería | Especificación analítica |
| [Reporte de Perfilado de Telemetría (Data Profile)](./data-profile.md) | Métricas descriptivas, rangos, conteos de cardinalidad, distribución de clases y validación UCI | Reporte generado automáticamente (**HU-02**) |

---

## 2. Generación del Reporte de Perfilado

El reporte [`data-profile.md`](./data-profile.md) se genera de forma determinista mediante el servicio de perfilado en Python:

```bash
# Desde la carpeta ml_service:
python -m src.cli profile

# O ejecutando el pipeline completo:
python -m src.cli all
```
