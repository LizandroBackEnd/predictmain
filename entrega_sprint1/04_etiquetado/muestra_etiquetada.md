# Muestra etiquetada del dataset AI4I 2020

Generada automáticamente por `scripts/generar_muestra_etiquetada.py` con `random_state=42`.

## 1. Archivos generados

| Archivo | Contenido | Registros |
| --- | --- | --- |
| `datos/datos_etiquetados.csv` | Dataset completo con etiquetas legibles | 10,000 |
| `datos/muestra_etiquetada.csv` | Muestra reproducible para revisión humana | 30 |

## 2. Dataset etiquetado completo

| Métrica | Valor |
| --- | --- |
| Registros | 10,000 |
| Fallas | 339 |
| Sin falla | 9,661 |
| Registros con al menos un modo activo | 348 |
| Registros con múltiples modos | 24 |
| Etiqueta 0 con modo activo | 18 |
| Etiqueta 1 sin modo activo | 9 |

## 3. Esquema del dataset etiquetado

| Columna | Descripción |
| --- | --- |
| `UDI` | Identificador único del registro. |
| `Product ID` | Identificador del producto. |
| `Type` | Tipo de producto: L, M o H. |
| Variables de sensores | Temperaturas, RPM, torque y desgaste. |
| `Machine failure` | Etiqueta original 0/1. |
| `TWF`, `HDF`, `PWF`, `OSF`, `RNF` | Modos de falla binarios. |
| `etiqueta` | Etiqueta legible: `Sin falla` o `Falla`. |
| `modos_activos` | Lista de modos activos o `Ninguno`. |

## 4. Muestra para revisión humana

- Registros de la muestra: **30**
- Fallas en la muestra: **15**
- Sin falla en la muestra: **15**

| UDI | Type | Air temperature [K] | Process temperature [K] | Rotational speed [rpm] | Torque [Nm] | Tool wear [min] | Machine failure | etiqueta | modos_activos |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 595 | H | 297.6 | 309.6 | 1278 | 50.4 | 2 | 0 | Sin falla | Ninguno |
| 5083 | H | 304.1 | 313.2 | 1590 | 43.4 | 52 | 0 | Sin falla | Ninguno |
| 8319 | H | 298.7 | 309.7 | 1565 | 39.3 | 94 | 0 | Sin falla | Ninguno |
| 8418 | H | 298.8 | 310.1 | 1704 | 30.7 | 150 | 0 | Sin falla | Ninguno |
| 9014 | H | 297.2 | 308.0 | 1435 | 43.0 | 202 | 0 | Sin falla | Ninguno |
| 3749 | L | 302.5 | 311.1 | 1493 | 39.0 | 137 | 0 | Sin falla | Ninguno |
| 6503 | L | 300.9 | 310.0 | 2595 | 13.7 | 207 | 0 | Sin falla | Ninguno |
| 7097 | L | 300.6 | 310.2 | 1489 | 47.8 | 21 | 0 | Sin falla | Ninguno |
| 7944 | L | 300.8 | 311.7 | 1753 | 29.0 | 8 | 0 | Sin falla | Ninguno |
| 8057 | L | 300.1 | 311.5 | 1499 | 43.4 | 65 | 0 | Sin falla | Ninguno |
| 2376 | M | 299.2 | 308.4 | 1476 | 32.7 | 101 | 0 | Sin falla | Ninguno |
| 5229 | M | 303.9 | 313.1 | 1343 | 61.4 | 14 | 0 | Sin falla | Ninguno |
| 5689 | M | 302.3 | 311.7 | 1423 | 44.6 | 93 | 0 | Sin falla | Ninguno |
| 6429 | M | 300.2 | 309.8 | 1743 | 24.1 | 18 | 0 | Sin falla | Ninguno |
| 8143 | M | 299.7 | 311.0 | 1448 | 49.8 | 80 | 0 | Sin falla | Ninguno |
| 1088 | H | 296.9 | 307.8 | 1549 | 35.8 | 206 | 1 | Falla | TWF |
| 1124 | H | 296.6 | 307.7 | 1386 | 62.3 | 100 | 1 | Falla | PWF |
| 3866 | H | 302.6 | 311.5 | 1629 | 34.4 | 228 | 1 | Falla | TWF |
| 4779 | H | 303.6 | 312.2 | 1371 | 54.6 | 112 | 1 | Falla | HDF |
| 5400 | H | 302.8 | 312.4 | 1411 | 53.8 | 246 | 1 | Falla | OSF |
| 328 | L | 297.7 | 308.5 | 1373 | 56.7 | 203 | 1 | Falla | OSF |
| 3944 | L | 302.3 | 311.4 | 1333 | 66.7 | 205 | 1 | Falla | PWF, OSF |
| 4597 | L | 303.0 | 311.2 | 1361 | 47.6 | 106 | 1 | Falla | HDF |
| 6498 | L | 300.8 | 309.9 | 1312 | 65.3 | 192 | 1 | Falla | OSF |
| 8358 | L | 298.5 | 309.5 | 1385 | 46.3 | 203 | 1 | Falla | TWF |
| 195 | M | 298.2 | 308.5 | 2678 | 10.7 | 86 | 1 | Falla | PWF |
| 3807 | M | 302.3 | 310.9 | 1360 | 44.0 | 67 | 1 | Falla | HDF |
| 4025 | M | 302.1 | 311.0 | 1351 | 60.3 | 207 | 1 | Falla | OSF |
| 4208 | M | 302.3 | 310.9 | 1710 | 30.4 | 218 | 1 | Falla | TWF |
| 4254 | M | 302.6 | 311.0 | 1329 | 48.6 | 111 | 1 | Falla | HDF |

## 5. Diccionario de etiquetas

| Etiqueta | Significado |
| --- | --- |
| Sin falla | `Machine failure = 0`; el registro no representa una falla operativa. |
| Falla | `Machine failure = 1`; el registro representa una falla operativa. |
| Ninguno | No se activó ningún modo de falla específico. |
| TWF | Tool Wear Failure: falla por desgaste de herramienta. |
| HDF | Heat Dissipation Failure: falla por disipación de calor. |
| PWF | Power Failure: falla por potencia. |
| OSF | Overstrain Failure: falla por sobreesfuerzo. |
| RNF | Random Failure: falla aleatoria. |

## 6. Reproducibilidad

```powershell
python scripts/generar_muestra_etiquetada.py
```

La muestra no se usa para entrenar; su propósito es facilitar la revisión y validación de etiquetas.
