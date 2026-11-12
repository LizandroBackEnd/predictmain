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
| Existe la muestra etiquetada | OK | datos/muestra_etiquetada.csv |
| Muestra etiquetada con 30 registros | OK | 30 registros |
| Muestra etiquetada con 15 fallas | OK | 15 fallas |

## 2. Distribución de etiquetas

| Etiqueta | Registros | Porcentaje |
| --- | --- | --- |
| Sin falla (0) | 9,661 | 96.61% |
| Falla (1) | 339 | 3.39% |

## 3. Distribución de modos de falla

| Modo | Registros |
| --- | --- |
| TWF | 46 |
| HDF | 115 |
| PWF | 95 |
| OSF | 98 |
| RNF | 19 |

## 4. Archivos etiquetados

| Archivo | Contenido | Registros |
| --- | --- | --- |
| `datos/datos_etiquetados.csv` | Dataset completo con etiquetas legibles | 10,000 |
| `datos/muestra_etiquetada.csv` | Muestra reproducible para revisión | 30 |

## 5. Observaciones

- La etiqueta `Machine failure` es la variable objetivo oficial del dataset.
- Los modos `TWF`, `HDF`, `PWF`, `OSF` y `RNF` son columnas auxiliares de diagnóstico y pueden solaparse.
- Se identificaron 18 registros con etiqueta 0 pero con algún modo activo.
- Se identificaron 9 registros con etiqueta 1 pero sin ningún modo activo.
- Estas 27 inconsistencias se conservan tal como aparecen en el dataset original y se documentan como limitación conocida.
- El dataset etiquetado completo conserva las 14 columnas originales y agrega `etiqueta` y `modos_activos`.
