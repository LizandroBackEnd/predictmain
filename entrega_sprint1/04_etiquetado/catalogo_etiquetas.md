# Catálogo de etiquetas

> Definición de la variable objetivo y de los modos de falla del AI4I 2020.

## 1. Variable objetivo

| Campo | Valor |
| :--- | :--- |
| Nombre | `Machine failure` |
| Tipo | Binaria |
| Valores | `0` = sin falla, `1` = falla |
| Registros totales | 10,000 |
| Registros con falla | 339 (3.39%) |
| Registros sin falla | 9,661 (96.61%) |
| Uso | Etiqueta principal para clasificación supervisada |

## 2. Etiquetas legibles

| Etiqueta | Valor de `Machine failure` | Significado |
| :--- | :--- | :--- |
| `Sin falla` | 0 | El registro no representa una falla operativa. |
| `Falla` | 1 | El registro representa una falla operativa. |

La columna `modos_activos` solo admite dos formas:

| Valor | Criterio de asignación |
| :--- | :--- |
| `Ninguno` | Todas las columnas `TWF`, `HDF`, `PWF`, `OSF` y `RNF` valen 0. |
| Lista de códigos | Códigos de los modos con valor 1, separados por `, ` y en el orden `TWF`, `HDF`, `PWF`, `OSF`, `RNF` (por ejemplo, `HDF, OSF`). |

`Ninguno` no puede combinarse con códigos. Cualquier otro valor se considera fuera del catálogo.

## 3. Modos de falla

Los modos de falla son columnas auxiliares de diagnóstico. No sustituyen a la variable objetivo y pueden solaparse en un mismo registro.

| Código | Nombre | Significado | Registros |
| :--- | :--- | :--- | :--- |
| `TWF` | Tool Wear Failure | Falla por desgaste de herramienta. | 46 |
| `HDF` | Heat Dissipation Failure | Falla por disipación de calor. | 115 |
| `PWF` | Power Failure | Falla por potencia. | 95 |
| `OSF` | Overstrain Failure | Falla por sobreesfuerzo. | 98 |
| `RNF` | Random Failure | Falla aleatoria. | 19 |

## 4. Distribución de la etiqueta objetivo

| Clase | Registros | Porcentaje |
| :--- | :--- | :--- |
| 0 (sin falla) | 9,661 | 96.61% |
| 1 (falla) | 339 | 3.39% |

## 5. Distribución por tipo de producto

| Tipo | Registros | Porcentaje |
| :--- | :--- | :--- |
| L | 6,000 | 60.00% |
| M | 2,997 | 29.97% |
| H | 1,003 | 10.03% |

## 6. Relación entre etiqueta y modos

| Situación | Registros |
| :--- | :--- |
| Registros con al menos un modo activo | 348 |
| Registros con más de un modo activo | 24 |
| Etiqueta 0 con algún modo activo (en los 18 casos, `RNF`) | 18 |
| Etiqueta 1 sin ningún modo activo | 9 |
| Total de inconsistencias | 27 |

## 7. Archivos etiquetados

| Archivo | Contenido | Registros |
| --- | --- | --- |
| `datos/datos_etiquetados.csv` | Dataset completo con `etiqueta` y `modos_activos`. | 10,000 |
| `datos/muestra_etiquetada.csv` | Muestra reproducible para revisión humana. | 30 |
| `muestra_etiquetada.md` | Documento con la muestra y el diccionario de etiquetas. | 30 |

## 8. Nota

Las 27 inconsistencias se conservan tal como aparecen en el dataset original. Se documentan como limitación conocida y se justifican en `reglas_etiquetado.md`.
