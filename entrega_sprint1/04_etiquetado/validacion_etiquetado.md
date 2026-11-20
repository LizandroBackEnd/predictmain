# Validación del etiquetado

Generada automáticamente por `scripts/validar_etiquetas.py`.

## 1. Verificaciones

| Verificación | Resultado | Detalle |
| --- | --- | --- |
| Etiqueta objetivo sin valores nulos | OK | 0 nulos |
| Etiqueta objetivo binaria | OK | valores 0 y 1 |
| Total de fallas igual a 339 | OK | 339 fallas |
| Tipos de producto válidos | OK | ['H', 'L', 'M'] |
| Modos de falla binarios | OK | TWF, HDF, PWF, OSF, RNF |
| Registros con al menos un modo activo | OK | 348 registros |
| Registros con múltiples modos activos | OK | 24 registros |
| Inconsistencias documentadas: objetivo 0 con modo activo | OK | 18 registros |
| Inconsistencias documentadas: objetivo 1 sin modo activo | OK | 9 registros |
| Total de inconsistencias etiqueta-modo | OK | 27 registros |
| Existe el dataset etiquetado completo | OK | datos/datos_etiquetados.csv |
| Dataset etiquetado con 10,000 registros | OK | 10,000 registros |
| Dataset etiquetado conserva 339 fallas | OK | 339 fallas |
| Columna etiqueta sin nulos | OK | 0 nulos |
| Columna modos_activos sin nulos | OK | 0 nulos |
| Etiqueta legible coincide con Machine failure | OK | mapeo consistente |
| Etiquetas dentro del catálogo | OK | 0 registros fuera del catálogo |
| Sin etiquetas contradictorias | OK | 0 contradicciones |
| Columnas originales conservadas sin cambios | OK | 14 columnas comparadas |
| Existe la muestra etiquetada | OK | datos/muestra_etiquetada.csv |
| Muestra etiquetada con 30 registros | OK | 30 registros |
| Muestra etiquetada con 15 fallas | OK | 15 fallas |
| Muestra trazable al dataset completo | OK | 0 registros no trazables |

## 2. Hallazgos por registro

Ejecutada: 0 registros fuera del catálogo, 0 etiquetas contradictorias y 0 registros de muestra no trazables.

## 3. Distribución de etiquetas

| Etiqueta | Registros | Porcentaje |
| --- | --- | --- |
| Sin falla (0) | 9,661 | 96.61% |
| Falla (1) | 339 | 3.39% |

## 4. Distribución de modos de falla

| Modo | Registros |
| --- | --- |
| TWF | 46 |
| HDF | 115 |
| PWF | 95 |
| OSF | 98 |
| RNF | 19 |

## 5. Archivos etiquetados

| Archivo | Contenido | Registros |
| --- | --- | --- |
| `datos/datos_etiquetados.csv` | Dataset completo con etiquetas legibles | 10,000 |
| `datos/muestra_etiquetada.csv` | Muestra reproducible para revisión | 30 |

## 6. Observaciones

- La etiqueta `Machine failure` es la variable objetivo oficial del dataset.
- Los modos `TWF`, `HDF`, `PWF`, `OSF` y `RNF` son columnas auxiliares de diagnóstico y pueden solaparse.
- Se identificaron 18 registros con etiqueta 0 pero con algún modo activo; en los 18 el modo activo es `RNF`.
- Se identificaron 9 registros con etiqueta 1 pero sin ningún modo activo.
- Estas 27 inconsistencias se conservan tal como aparecen en el dataset original y se documentan como limitación conocida.
- El dataset etiquetado completo conserva las 14 columnas originales y agrega `etiqueta` y `modos_activos`.
