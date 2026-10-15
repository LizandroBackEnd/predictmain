# Roles y Stakeholders - PredictMain

> Definición de usuarios objetivo, interesados clave y matriz de responsabilidades del proyecto.

---

## 1. Segmento de Mercado y Usuarios Objetivo

El producto está diseñado para el sector industrial manufacturero, enfocado en:

- **Pequeñas y medianas empresas (PyMEs) industriales:** Organizaciones con maquinaria crítica cuyos costos por paros no planificados impactan severamente su rentabilidad.
- **Plantas de producción:** Instalaciones con procesos continuos que buscan transicionar de un mantenimiento reactivo a uno predictivo basado en condición.
- **Áreas operativas:** Departamentos de mantenimiento, confiabilidad y gestión de activos industriales.

---

## 2. Stakeholders Principales

A continuación se detallan los interesados del proyecto de acuerdo con la especificación formal:

| Stakeholder | Interés o Responsabilidad | Tipo de Participación |
| :--- | :--- | :--- |
| **Gerente o Responsable de Planta** | Requiere visibilidad global del estado de la maquinaria para reducir paros no programados, planificar presupuestos y tomar decisiones operativas de alto impacto. | Cliente, patrocinador (sponsor) y tomador de decisiones. |
| **Ingeniero de Mantenimiento** | Supervisa el estado de los equipos en piso, evalúa niveles de riesgo de falla calculados por el sistema, atiende alertas y ejecuta órdenes de trabajo. | Usuario principal del producto en el día a día. |
| **Ing. Erick Giovanni Valentino Salado** | Valida el significado físico de las variables de telemetría (temperatura, torque, revoluciones, desgaste), define rangos operativos seguros y asegura la consistencia técnica de las reglas desde el dominio industrial y químico. | Experto del dominio (Subject Matter Expert) y validador técnico. |
| **Analista o Científico de Datos** | Responsable de la exploración, limpieza, ingeniería de características, entrenamiento y evaluación de los modelos predictivos de Machine Learning. | Responsable del componente de Inteligencia Artificial. |

---

## 3. Matriz de Responsabilidades (RACI)

| Actividad / Decisión | Gerente de Planta | Ingeniero de Mantenimiento | Experto de Dominio | Científico de Datos |
| :--- | :---: | :---: | :---: | :---: |
| Definición de objetivos de negocio y prioridades | **A / R** | C | C | I |
| Validación de variables físicas y umbrales de alerta | I | R | **A** | C |
| Ingesta, perfilado y preparación del dataset AI4I 2020 | I | I | C | **A / R** |
| Entrenamiento y validación del modelo de predicción | I | I | C | **A / R** |
| Operación diaria del tablero y atención de alertas | I | **A / R** | C | I |
| Emisión y seguimiento de órdenes de trabajo (PDF) | I | **A / R** | I | I |

*Convenciones: **R** (Responsible), **A** (Accountable / Aprobador), **C** (Consulted), **I** (Informed).*
