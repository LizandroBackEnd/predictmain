# Reporte de Análisis de Valores Atípicos — HU-05

> Generado automáticamente por el pipeline de análisis de PredictMain.

---

## 1. Resumen Ejecutivo

| Métrica | Valor |
| :--- | :--- |
| Archivo analizado | `ai4i2020_clean.csv` |
| Fecha de ejecución | 2026-11-10 13:53:25 UTC |
| Registros de entrada | 10,000 |
| Registros de salida | 10,000 |
| Total outliers detectados (unión IQR+P1/P99) | 1,170 |
| Total valores modificados (CAP) | 0 |
| Total filas excluidas | 0 |

> **Principio:** Los outliers NO se eliminan automáticamente. Cada decisión está justificada con criterios del dominio físico.

---

## 2. Detección por Columna — IQR y Percentiles

| Variable | Q1 | Q3 | IQR | Fence Low | Fence High | IQR outliers | P1 | P99 | P1/P99 outliers | Fuera rango UCI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Air temperature [K]` | 298.30 | 301.50 | 3.20 | 293.50 | 306.30 | 0 | 295.90 | 304.10 | 162 | 0 |
| `Process temperature [K]` | 308.80 | 311.10 | 2.30 | 305.35 | 314.55 | 0 | 306.60 | 313.20 | 195 | 0 |
| `Rotational speed [rpm]` | 1423.00 | 1612.00 | 189.00 | 1139.50 | 1895.50 | 418 | 1275.00 | 2188.01 | 198 | 0 |
| `Torque [Nm]` | 33.20 | 46.80 | 13.60 | 12.80 | 67.20 | 69 | 16.70 | 62.80 | 198 | 0 |
| `Tool wear [min]` | 53.00 | 162.00 | 109.00 | -110.50 | 325.50 | 0 | 0.00 | 222.00 | 99 | 0 |

---

## 3. Decisión por Variable — Regla → Decisión → Conteos

| Variable | Tipo de atípico | Detección | Decisión | Detectados | Modificados | Excluidos |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Air temperature [K]` | valid_extreme | IQR+PERCENTILE | **KEEP** | 162 | 0 | 0 |
| `Process temperature [K]` | valid_extreme | IQR+PERCENTILE | **KEEP** | 195 | 0 | 0 |
| `Rotational speed [rpm]` | failure_signal | IQR+PERCENTILE | **KEEP** | 516 | 0 | 0 |
| `Torque [Nm]` | failure_signal | IQR+PERCENTILE | **KEEP** | 198 | 0 | 0 |
| `Tool wear [min]` | valid_extreme | IQR+PERCENTILE | **KEEP** | 99 | 0 | 0 |

---

## 4. Justificación Técnica por Variable

### `Air temperature [K]`

- **Decisión:** KEEP
- **Tipo:** valid_extreme
- **Rango físico UCI:** [295.3, 304.5]
- **Justificación:** Air temperature varies naturally with ambient plant conditions. IQR detects 0 outliers — the distribution is compact (σ≈2K). P1/P99 detects 162 values but all fall within the UCI physical range [295.3K–304.5K], confirming they are valid ambient readings, not sensor errors. Decision: KEEP — no transformation applied.

### `Process temperature [K]`

- **Decisión:** KEEP
- **Tipo:** valid_extreme
- **Rango físico UCI:** [305.7, 313.8]
- **Justificación:** Process temperature reflects friction from the manufacturing process. IQR detects 0 outliers. P1/P99 flags 195 values, all within the UCI physical range [305.7K–313.8K]. These represent genuine high-friction operating cycles, not measurement artifacts. Decision: KEEP — values are physically meaningful.

### `Rotational speed [rpm]`

- **Decisión:** KEEP
- **Tipo:** failure_signal
- **Rango físico UCI:** [1168.0, 2886.0]
- **Justificación:** IQR (fence: 1139–1895 rpm) flags 418 records above 1895 rpm. These high-speed readings correlate with power failure (PWF) events where the motor overrevs before shutdown. Eliminating them would remove critical failure-precursor signals. All values are within the UCI physical range [1168–2886 rpm]. Decision: KEEP — statistical outliers are domain-valid failure signals.

### `Torque [Nm]`

- **Decisión:** KEEP
- **Tipo:** failure_signal
- **Rango físico UCI:** [3.8, 76.6]
- **Justificación:** IQR (fence: 12.8–67.2 Nm) flags 69 records. Low-torque extremes correspond to PWF (power failure) conditions; high-torque extremes correspond to OSF (overstrain failure) precursors. Both carry predictive value for the ML model. All values are within the UCI physical range [3.8–76.6 Nm]. Decision: KEEP — extremes represent genuine failure-mode signatures.

### `Tool wear [min]`

- **Decisión:** KEEP
- **Tipo:** valid_extreme
- **Rango físico UCI:** [0.0, 253.0]
- **Justificación:** IQR fence is [-110.5, 325.5 min] — wider than the physical range, so IQR detects 0 outliers. P1/P99 flags 99 high-wear values (>230 min). High tool wear is physically expected before a TWF (tool wear failure) event and is the primary feature for that failure mode. All values are within UCI physical range [0–253 min]. Decision: KEEP — high wear is a direct failure-precursor feature.

---

## 5. Conclusión

Se analizaron **5 variables** de sensores. Se detectaron **1,170 valores atípicos** en total (unión de IQR 1.5× y percentiles P1/P99). 
**Todos los outliers fueron conservados (KEEP):** representan señales físicas válidas o precursores de falla con valor predictivo para el modelo.

---

> **Reporte generado:** 2026-11-10 13:53:25 UTC
