# Capacidades del Producto - PredictMain

> Especificación de las funcionalidades y capacidades operativas del sistema.

---

## 1. Catálogo de Capacidades

PredictMain integra en un único entorno la gestión de activos, la telemetría operativa y el análisis de riesgo asistido por inteligencia artificial.

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        Capacidades PredictMain                         │
├───────────────────┬───────────────────┬────────────────────────────────┤
│    Operativas     │    Analíticas     │         Administrativas        │
├───────────────────┼───────────────────┼────────────────────────────────┤
│ • Gestión Activos │ • Riesgo de Falla │ • Generación de Bitácoras PDF  │
│ • Ingesta Sensores│ • Tendencias      │ • Órdenes de Trabajo PDF       │
│ • Monitoreo Vivo  │ • Detección Outlier│ • Asistente RAG de Manuales   │
│ • Alertas Umbral  │ • Inferencia ML   │ • Historial de Intervenciones  │
└───────────────────┴───────────────────┴────────────────────────────────┘
```

---

## 2. Detalle de Capacidades Funcionales

### 2.1 Gestión del Catálogo de Activos
- **Jerarquía industrial:** Registro estructurado de plantas, clientes, tipos de producto (L - Low, M - Medium, H - High) y maquinaria.
- **Ficha técnica:** Identificador único, fabricante, fecha de instalación y parámetros nominales de operación.

### 2.2 Ingesta de Telemetría Multivariable
- **Recepción de variables críticas:**
  - Temperatura del aire [K].
  - Temperatura del proceso [K].
  - Velocidad de rotación [RPM].
  - Torque mecánico [Nm].
  - Desgaste acumulado de la herramienta (*tool wear*) [min].
- **Validación estructural:** Verificación de rangos físicos e identificación de datos corruptos o fuera de escala en la ingesta.

### 2.3 Cálculo de Desgaste y Riesgo de Falla
- **Motor de inferencia:** Evaluación automatizada del estado de la máquina a través del modelo de Machine Learning entrenado.
- **Indicador de riesgo porcentual:** Cuantificación probabilística del riesgo de fallo inminente para facilitar la priorización operativa.
- **Tipificación de fallas potenciales:** Detección de patrones asociados a modos de fallo mecánicos (desgaste de herramienta, disipación de calor, falla de potencia, sobreesfuerzo).

### 2.4 Tablero de Monitoreo en Tiempo Real
- **Semáforo de condición:** Indicador visual inmediato del estado de cada máquina (Normal, Advertencia, Crítico).
- **Filtro de criticidad:** Visualización prioritaria de equipos que requieren atención urgente o inspección en planta.

### 2.5 Análisis de Tendencias y Umbrales Críticos
- **Gráficas de series temporales:** Representación histórica interactiva de variables físicas (temperatura, revoluciones, torque).
- **Proyección de desgaste:** Comparación visual contra límites operativos de ingeniería y umbrales de alerta temprana.

### 2.6 Generación de Documentación Operativa (PDF)
- **Bitácoras de mantenimiento:** Exportación en PDF con resumen de telemetría reciente y eventos registrados.
- **Órdenes de trabajo preventivas:** Creación de hojas de servicio pre-llenadas con diagnóstico preliminar y recomendaciones de inspección.

### 2.7 Historial y Trazabilidad de Eventos
- Registro cronológico inalterable de lecturas anómalas, alertas disparadas y notas de mantenimiento ingresadas por los operadores.

### 2.8 Configuración Dinámica de Umbrales
- Ajuste granular de límites operativos de temperatura, torque y vibración según las especificaciones del fabricante y la recomendación del experto de dominio.
