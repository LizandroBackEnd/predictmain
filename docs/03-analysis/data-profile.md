# Reporte de Perfilado de Telemetría Histórica — ai4i2020.csv

> Documento generado automáticamente por el servicio de perfilado de PredictMain (HU-02).

---

## 1. Resumen Dimensional

- **Archivo analizado:** `ai4i2020.csv`
- **Total de registros:** 10,000
- **Total de columnas:** 14

## 2. Estadísticas de Variables Numéricas Operativas

| Variable | Mínimo | Máximo | Media | Mediana | Desv. Estándar | Únicos |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `Air temperature [K]` | 295.30 | 304.50 | 300.00 | 300.10 | 2.00 | 93 |
| `Process temperature [K]` | 305.70 | 313.80 | 310.01 | 310.10 | 1.48 | 82 |
| `Rotational speed [rpm]` | 1,168.00 | 2,886.00 | 1,538.78 | 1,503.00 | 179.28 | 941 |
| `Torque [Nm]` | 3.80 | 76.60 | 39.99 | 40.10 | 9.97 | 577 |
| `Tool wear [min]` | 0.00 | 253.00 | 107.95 | 108.00 | 63.65 | 246 |

## 3. Distribución de Variables Categóricas

| Variable | Valores Únicos | Distribución |
| :--- | :--- | :--- |
| `Type` | 3 | L: 6,000, M: 2,997, H: 1,003 |

## 4. Distribución de la Variable Objetivo y Modos de Falla

| Variable Objetivo | Clase 0 (Normal) | Clase 1 (Falla) | % Falla |
| :--- | :--- | :--- | :--- |
| `Machine failure` | 9,661 | 339 | 3.39% |

### Modos Específicos de Falla Mecánica

| Modo de Falla | Ocurrencias | % Incidencia |
| :--- | :--- | :--- |
| `TWF` | 46 | 0.46% |
| `HDF` | 115 | 1.15% |
| `PWF` | 95 | 0.95% |
| `OSF` | 98 | 0.98% |
| `RNF` | 19 | 0.19% |

## 5. Control de Calidad contra Ficha Técnica UCI

| Criterio | Observado | Estado |
| :--- | :--- | :--- |
| Total registros | 10,000 | ✅ Coincide con UCI (10,000) |
| Total columnas | 14 | ✅ Coincide con UCI (14) |
| Valores nulos totales | 0 | ✅ Sin valores faltantes en capa raw |
| Categoría Type | L, M, H | ✅ Válido (50% L, 30% M, 20% H) |
| Variables continuas físicas | Temp [K], RPM, Torque, Wear | ✅ Unidades y rangos válidos |

## 6. Variables Candidatas para Modelado Predictivo

| Variable | Rol en Modelado | Consideración de Ingeniería |
| :--- | :--- | :--- |
| `Air temperature [K]` | Predictora continua | Temperatura ambiente en planta. |
| `Process temperature [K]` | Predictora continua | Fricción de manufactura; relación térmica directa. |
| `Rotational speed [rpm]` | Predictora continua | Velocidad del husillo. |
| `Torque [Nm]` | Predictora continua | Fuerza mecánica aplicada. |
| `Tool wear [min]` | Predictora continua | Desgaste de herramienta acumulado. |
| `Type` | Predictora categórica | Variante de producto (L, M, H) a codificar mediante One-Hot. |
| `UDI` / `Product ID` | Identificadores (Excluir) | No predictivos; evitan fuga de información. |
| `TWF`, `HDF`, `PWF`, `OSF`, `RNF` | Etiquetas auxiliares | Modos de falla para análisis multietiqueta futuro. |

## 7. Conclusión

El dataset AI4I 2020 se encuentra validado y listo para la fase de preparación y modelado sin inconsistencias estructurales.
