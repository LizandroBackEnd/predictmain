# Acta de Constitución del Proyecto (Project Charter)

> PredictMain: Plataforma web de mantenimiento predictivo basada en inteligencia artificial.

---

## 1. Información General del Proyecto

- **Nombre del Proyecto:** PredictMain
- **Institución:** Universidad Tecnológica de Nezahualcóyotl (UTN)
- **División Académica:** División de Tecnologías de la Información
- **Carrera:** Licenciatura en Ingeniería en Tecnologías de la Información e Innovación Digital
- **Asignatura:** Formulación de Proyectos de Tecnología
- **Docente:** Profr. Contreras Trejo Esmeralda
- **Grupo:** G050-701M
- **Fecha de Aprobación Inicial:** 29 de septiembre de 2026
- **Versión del Documento Base:** 1.0

### Equipo de Desarrollo

| Nombre del Alumno | Matrícula | Rol Principal |
| :--- | :--- | :--- |
| **Antonio Santos Lizandro** | 243105003 | Arquitecto de Software & Tech Lead |
| **Baez García Fátima Guadalupe** | 243105007 | Ingeniera de Requerimientos & QA |
| **Bautista Patiño Luis Antonio** | 243105179 | Desarrollador Backend & Datos |
| **Cruz Jaime Jessica Beatriz** | 243105009 | Desarrolladora Frontend & UI/UX |
| **Mérida López María Isabel** | 243105012 | Analista de Datos & Documentación |

---

## 2. Contexto y Justificación

En las pequeñas y medianas empresas industriales, el mantenimiento de maquinaria suele realizarse de forma reactiva (atender la falla cuando la máquina ya se detuvo) o con base en calendarios fijos desvinculados del desgaste real.

Esta situación genera:
1. **Paros no planificados:** Detención imprevista de líneas de producción con pérdidas económicas directas.
2. **Dispersión de telemetría:** Variables críticas como temperatura, revoluciones por minuto y torque son registradas en papel, de manera aislada, o no se analizan sistemáticamente.
3. **Decisiones a ciegas:** Falta de herramientas analíticas para predecir cuándo un componente alcanzará su umbral de ruptura.

**PredictMain** nace como una iniciativa de transformación digital para convertir las lecturas de telemetría en pronósticos oportunos de falla mecánica mediante modelos supervisados de Machine Learning.

---

## 3. Objetivos del Proyecto

### 3.1 Objetivo General
Desarrollar una plataforma web de mantenimiento predictivo que utilice datos de telemetría y técnicas de análisis e inteligencia artificial para estimar el desgaste y el riesgo de falla de maquinaria industrial, facilitando el monitoreo, la generación de alertas y la toma oportuna de decisiones de mantenimiento.

### 3.2 Objetivos Específicos

1. **Centralizar** el registro y la administración de los activos industriales que serán monitoreados.
2. **Incorporar** datos operativos de las máquinas, incluyendo temperatura ambiente, temperatura de proceso, RPM y torque.
3. **Analizar** los datos disponibles para calcular indicadores de desgaste y riesgo de falla.
4. **Proporcionar tableros** visuales que permitan conocer el estado operativo de las máquinas de forma clara y oportuna.
5. **Mostrar tendencias** históricas y umbrales críticos para facilitar la identificación de comportamientos anómalos.
6. **Generar alertas** automáticas cuando las condiciones operativas indiquen un posible riesgo de avería.
7. **Facilitar la consulta** del historial de alertas y bitácoras de intervenciones técnicas.
8. **Generar bitácoras y órdenes de trabajo** en formato PDF para formalizar la gestión del mantenimiento.
9. **Validar la solución** utilizando inicialmente el *AI4I 2020 Predictive Maintenance Dataset*.
10. **Establecer una base tecnológica robusta** que permita evolucionar la solución hacia escenarios industriales conectados en planta.

---

## 4. Enfoque Metodológico

El proyecto adopta un enfoque híbrido que garantiza rigor en la ciencia de datos y agilidad en la entrega de software:

- **CRISP-DM (Cross-Industry Standard Process for Data Mining):** Guía el ciclo de vida del componente analítico (Comprensión del Negocio $\rightarrow$ Comprensión de Datos $\rightarrow$ Preparación $\rightarrow$ Modelado $\rightarrow$ Evaluación $\rightarrow$ Despliegue).
- **Scrum / Agile:** Enmarca los sprints de desarrollo de la plataforma web, asegurando entregas incrementales y trazabilidad en historias de usuario.
