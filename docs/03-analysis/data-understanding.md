# Comprensión y Análisis de Datos (Data Understanding) - PredictMain

> Especificación del conjunto de datos base: AI4I 2020 Predictive Maintenance Dataset.

---

## 1. Origen del Dataset

El proyecto utiliza inicialmente el conjunto de datos sintético pero realista **AI4I 2020 Predictive Maintenance Dataset** (disponible en el repositorio UCI Machine Learning), diseñado específicamente para reflejar condiciones operativas reales de maquinaria de fresado y torneado industrial.

- **Total de instancias:** 10,000 registros de funcionamiento.
- **Variables predictoras:** 6 variables continuas y categóricas.
- **Variable objetivo principal:** `Machine failure` (0: Funcionamiento normal, 1: Falla mecánica).
- **Modos de fallo independientes:** 5 variables binarias indicadoras de la causa de falla.

---

## 2. Diccionario de Variables

| Variable | Tipo de Dato | Unidad | Descripción en el Dominio Industrial |
| :--- | :--- | :---: | :--- |
| `UDI` | Identificador | Entero | Identificador secuencial del registro (1 a 10,000). |
| `Product ID` | Categórico | Texto | Código de variante compuesto por la letra del tipo (`L`, `M`, `H`) y un número de serie. |
| `Type` | Categórico | Letra | Calidad o variante del producto procesado: **L** (Low - 50%), **M** (Medium - 30%), **H** (High - 20%). |
| `Air temperature [K]` | Numérico | Kelvin | Temperatura del aire ambiental en la planta industrial. |
| `Process temperature [K]` | Numérico | Kelvin | Temperatura generada por la fricción y el proceso de manufactura. |
| `Rotational speed [rpm]` | Numérico | RPM | Velocidad angular del eje de la máquina calculada a partir de una potencia de 2860 W. |
| `Torque [Nm]` | Numérico | Newton metro | Fuerza de torsión aplicada sobre la herramienta de corte. |
| `Tool wear [min]` | Numérico | Minutos | Tiempo acumulado de uso de la herramienta de corte (las variantes H/M/L añaden diferente ritmo de desgaste). |
| `Machine failure` | Binario (Objetivo) | 0 / 1 | Etiqueta principal que indica si la máquina experimentó una falla durante el ciclo. |

---

## 3. Modos de Fallo Específicos

El dataset documenta 5 causas mecánicas independientes de detención:

1. **TWF (Tool Wear Failure - Falla por Desgaste de Herramienta):** Ocurre cuando el tiempo de uso excede los límites admisibles de vida útil (usualmente entre 200 y 240 minutos).
2. **HDF (Heat Dissipation Failure - Falla por Disipación de Calor):** Provocada cuando la diferencia de temperatura entre el proceso y el aire ambiental es inferior a 8.6 K y la velocidad de rotación es baja (< 1380 RPM).
3. **PWF (Power Failure - Falla de Potencia):** Se genera cuando la potencia mecánica requerida (producto de torque y velocidad angular) excede los 9,000 W o cae por debajo de 3,500 W.
4. **OSF (Overstrain Failure - Falla por Sobreesfuerzo):** Sucede cuando el producto del desgaste de la herramienta y el torque supera los umbrales críticos de resistencia del material según la variante (`L`, `M`, `H`).
5. **RNFP (Random Failure - Falla Aleatoria):** Evento estocástico que ocurre con una probabilidad intrínseca menor al 0.1 %, independiente de las condiciones operativas registradas.

---

## 4. Retos y Consideraciones Técnicas

- **Fuerte Desbalance de Clases:** En el dataset original, únicamente ~3.39% de los registros corresponden a fallas (`Machine failure = 1`). Esto requiere estrategias de muestreo estratificado (`StratifiedKFold`), evaluación con métricas sensibles (PR-AUC, F1-Score, Recall) y ajuste de pesos en los clasificadores.
- **Fuga de Información (*Data Leakage*):** Las columnas correspondientes a los modos de falla (`TWF`, `HDF`, `PWF`, `OSF`, `RNFP`) no deben ser utilizadas como variables predictoras durante la inferencia en tiempo real, ya que solo se conocen posterior al evento de falla.
