# Reglas de etiquetado

> Criterios aplicados para interpretar y validar las etiquetas del AI4I 2020.

## 1. Regla principal

La etiqueta objetivo se toma directamente de la columna `Machine failure`:

```text
si Machine failure == 1 -> etiqueta "Falla"
si Machine failure == 0 -> etiqueta "Sin falla"
```

No se infiere la etiqueta a partir de los modos de falla. La columna `Machine failure` es la fuente de verdad para el entrenamiento supervisado.

## 2. Reglas de los modos de falla

Cada modo (`TWF`, `HDF`, `PWF`, `OSF`, `RNF`) es una columna binaria:

```text
0 -> modo no activo
1 -> modo activo
```

Los modos pueden solaparse. Un registro puede tener varios modos activos y sigue contando como una sola falla en `Machine failure`.

## 3. Reglas de validación

| Regla | Criterio | Resultado |
| :--- | :--- | :--- |
| Etiqueta sin nulos | `Machine failure` no debe tener nulos | OK |
| Etiqueta binaria | Solo valores 0 y 1 | OK |
| Total de fallas | 339 registros con etiqueta 1 | OK |
| Tipos válidos | `Type` en {L, M, H} | OK |
| Modos binarios | Cada modo en {0, 1} | OK |
| Al menos un modo activo | 348 registros | OK |
| Múltiples modos | 24 registros | OK |
| Consistencia etiqueta-modo | 27 inconsistencias documentadas | OK |

## 4. Inconsistencias conocidas

### 4.1 Etiqueta 0 con modo activo

- **Registros:** 18.
- **Situación:** `Machine failure = 0` pero al menos un modo de falla está activo.
- **Causa probable:** los modos de falla se registran de forma independiente y no siempre actualizan la etiqueta principal.
- **Decisión:** conservar el registro y respetar `Machine failure` como etiqueta objetivo.

### 4.2 Etiqueta 1 sin modo activo

- **Registros:** 9.
- **Situación:** `Machine failure = 1` pero ningún modo específico está activo.
- **Causa probable:** falla registrada sin clasificación de modo, o falla aleatoria no reflejada en `RNF`.
- **Decisión:** conservar el registro y respetar `Machine failure` como etiqueta objetivo.

## 5. Tratamiento de `RNF`

`RNF` (Random Failure) presenta 19 registros activos:

- 18 tienen `Machine failure = 0`.
- 1 tiene `Machine failure = 1`.

Los 18 registros con `RNF = 1` y `Machine failure = 0` son exactamente las 18 inconsistencias de la sección 4.1; ningún otro modo aparece activo con etiqueta 0. No se corrige el dato original.

## 6. Decisiones de etiquetado

1. No se eliminan registros inconsistentes.
2. No se reetiquetan registros manualmente.
3. No se usan los modos como variable objetivo.
4. Los modos se reservan para análisis de diagnóstico y posible modelado multietiqueta futuro.
5. La etiqueta `Machine failure` se conserva idéntica en todas las etapas del pipeline.

## 7. Justificación de la estrategia

La estrategia utiliza `Machine failure` como etiqueta supervisada porque es la variable oficial del dataset y la que representa el evento operativo que el modelo debe anticipar. Los modos de falla no se usan como objetivo por tres razones:

1. **Jerarquía del dato:** `Machine failure` es la etiqueta agregada; los modos son columnas auxiliares de diagnóstico.
2. **Fuga de información:** usar los modos como entradas o como objetivo podría filtrar la causa de la falla y reducir la utilidad predictiva.
3. **Consistencia metodológica:** entrenar con una sola etiqueta binaria permite comparar modelos, métricas y umbrales de forma directa.

Las 27 inconsistencias se conservan porque eliminar o reetiquetar registros introduciría decisiones no respaldadas por el dataset original. En su lugar, se documentan como limitación y se validan automáticamente para que cualquier cambio futuro sea detectable.

La muestra de 30 registros se genera con `random_state=42` y una distribución equilibrada por clase y tipo. No se usa para entrenar: su función es permitir revisión humana y demostrar que el etiquetado es reproducible.

## 8. Validación de consistencia

La validación automática comprueba:

- Que la etiqueta objetivo no tenga nulos y sea binaria.
- Que el total de fallas sea 339.
- Que los tipos de producto y los modos sean válidos.
- Que se conserven 348 registros con al menos un modo activo y 24 con múltiples modos.
- Que las 18 inconsistencias de etiqueta 0 con modo activo y las 9 de etiqueta 1 sin modo activo sigan documentadas.
- Que el dataset etiquetado completo tenga 10,000 registros y conserve 339 fallas.
- Que la columna `etiqueta` coincida exactamente con el mapeo de `Machine failure`.
- Que cada valor de `etiqueta` y `modos_activos` pertenezca al catálogo (`catalogo_etiquetas.md`).
- Que ninguna etiqueta contradiga sus columnas de origen: `etiqueta` frente a `Machine failure` y `modos_activos` frente a `TWF`, `HDF`, `PWF`, `OSF` y `RNF`.
- Que las 14 columnas originales del dataset etiquetado sean idénticas al dataset crudo.
- Que la muestra tenga 30 registros y 15 fallas, y que cada registro coincida con el dataset completo.

Un valor fuera del catálogo o una etiqueta contradictoria hace fallar la validación. El reporte identifica el `UDI`, la columna y el valor afectado, y el valor no se convierte a una categoría conocida: queda registrado para su corrección.

Resultado: **23 de 23 verificaciones aprobadas**.

## 9. Evidencia

- Dataset etiquetado completo: `datos/datos_etiquetados.csv`.
- Muestra etiquetada: `datos/muestra_etiquetada.csv`.
- Documento de muestra: `muestra_etiquetada.md`.
- Validación automática: `validacion_etiquetado.md`.
- Log de validación: `evidencias/validacion_etiquetado.log`.
- Reporte de perfilado: `03_dataset/data/profiling/data-profile-2026-11-11.md`.
