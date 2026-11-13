# Reporte de Tratamiento de Valores Nulos — HU-04

> Generado automáticamente por el pipeline de tratamiento de PredictMain.

---

## 1. Resumen Ejecutivo

| Métrica | Valor |
| :--- | :--- |
| Archivo fuente | `ai4i2020.csv` |
| Archivo depurado | `ai4i2020_clean.csv` |
| Fecha de ejecución | 2026-11-13 00:07:33 UTC |
| Filas antes del tratamiento | 10,000 |
| Filas con al menos un nulo | 0 |
| Total de valores nulos encontrados | 0 |
| Filas eliminadas (labels nulos) | 0 |
| Valores imputados | 0 |
| Filas en dataset depurado | 10,000 |

> ✅ **El dataset no contenía valores nulos.** No se realizaron imputaciones ni eliminaciones.

## 2. Detalle por Columna — Antes y Después

| Columna | Nulos antes | % Nulos | Decisión | Estrategia | Imputados | Filas eliminadas |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `UDI` | 0 | 0.00% | KEEP | — | 0 | 0 |
| `Product ID` | 0 | 0.00% | KEEP | — | 0 | 0 |
| `Type` | 0 | 0.00% | IMPUTE | mode | 0 | 0 |
| `Air temperature [K]` | 0 | 0.00% | IMPUTE | median | 0 | 0 |
| `Process temperature [K]` | 0 | 0.00% | IMPUTE | median | 0 | 0 |
| `Rotational speed [rpm]` | 0 | 0.00% | IMPUTE | median | 0 | 0 |
| `Torque [Nm]` | 0 | 0.00% | IMPUTE | median | 0 | 0 |
| `Tool wear [min]` | 0 | 0.00% | IMPUTE | median | 0 | 0 |
| `Machine failure` | 0 | 0.00% | DROP_ROW | — | 0 | 0 |
| `TWF` | 0 | 0.00% | DROP_ROW | — | 0 | 0 |
| `HDF` | 0 | 0.00% | DROP_ROW | — | 0 | 0 |
| `PWF` | 0 | 0.00% | DROP_ROW | — | 0 | 0 |
| `OSF` | 0 | 0.00% | DROP_ROW | — | 0 | 0 |
| `RNF` | 0 | 0.00% | DROP_ROW | — | 0 | 0 |

## 3. Justificación Técnica de las Reglas

| Columna | Decisión | Justificación |
| :--- | :--- | :--- |
| `UDI` | KEEP | Sequential identifier — not a model feature; never imputed. |
| `Product ID` | KEEP | Composite identifier — not a model feature; never imputed. |
| `Type` | IMPUTE | Categorical variable with 3 known classes (L, M, H). Most-frequent (mode) imputation preserves the empirical class prior without introducing an artificial new category. |
| `Air temperature [K]` | IMPUTE | Continuous sensor reading measured in Kelvin. Median is robust to transient sensor spikes that may have caused the gap and avoids inflating the mean under a slightly right-skewed distribution. |
| `Process temperature [K]` | IMPUTE | Continuous process sensor. Same rationale as air temperature: median guards against outlier influence while preserving the central tendency. |
| `Rotational speed [rpm]` | IMPUTE | Continuous motor speed variable. Median avoids inflating the estimate when the motor was at standstill (RPM ≈ 0) during the missing period. |
| `Torque [Nm]` | IMPUTE | Continuous mechanical variable with a long right tail. Median is more representative of typical operating torque than the mean. |
| `Tool wear [min]` | IMPUTE | Cumulative tool-use counter. Median of the distribution provides a conservative and physically plausible estimate for a missing cycle. |
| `Machine failure` | DROP_ROW | Primary target label for supervised learning. A missing label makes the record untrainable and undefinable; the row must be discarded entirely. |
| `TWF` | DROP_ROW | Failure-mode label — same rationale as Machine failure. |
| `HDF` | DROP_ROW | Failure-mode label — same rationale as Machine failure. |
| `PWF` | DROP_ROW | Failure-mode label — same rationale as Machine failure. |
| `OSF` | DROP_ROW | Failure-mode label — same rationale as Machine failure. |
| `RNF` | DROP_ROW | Failure-mode label — same rationale as Machine failure. |

## 4. Conclusión

El dataset depurado contiene **10,000 registros** listos para la fase de transformación (HU-05). 
No se requirió ninguna modificación: el dataset estaba completo.

---

> **Reporte generado:** 2026-11-13 00:07:33 UTC
