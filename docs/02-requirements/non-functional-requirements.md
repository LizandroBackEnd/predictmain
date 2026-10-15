# Requerimientos No Funcionales - PredictMain

> Condiciones de calidad, reproducibilidad, mantenibilidad, fiabilidad, observabilidad y seguridad técnica (RNF-01 a RNF-12).

---

## 1. Matriz de Requerimientos No Funcionales

| ID | Requerimiento No Funcional | Categoría | Prioridad |
| :--- | :--- | :---: | :---: |
| **RNF-01** | El pipeline debe ser reproducible utilizando código, configuración y dependencias versionadas. | Mantenibilidad | **P0 — Crítica** |
| **RNF-02** | El dataset original debe conservarse sin modificaciones y con trazabilidad de origen y versión. | Trazabilidad | **P0 — Crítica** |
| **RNF-03** | Las transformaciones deben ajustarse únicamente con los datos de entrenamiento para evitar fuga de información (*data leakage*). | Calidad del modelo | **P0 — Crítica** |
| **RNF-04** | El código de procesamiento debe utilizar Python y mantener compatibilidad con Pandas, NumPy y Scikit-learn. | Compatibilidad | **P0 — Crítica** |
| **RNF-05** | Las ejecuciones repetidas con la misma versión de datos y semilla (*seed*) deben producir resultados reproducibles, salvo diferencias justificadas del entorno. | Reproducibilidad | **P0 — Crítica** |
| **RNF-06** | El pipeline y el modelo deben poder ejecutarse sin errores en el entorno documentado del proyecto. | Fiabilidad | **P1 — Alta** |
| **RNF-07** | El modelo y el preprocesador deben conservarse como un artefacto reutilizable en formato `.pkl` o `.joblib` cuando se implemente el guardado. | Portabilidad | **P1 — Alta** |
| **RNF-08** | El código debe mantenerse bajo control de versiones mediante Git y alojado en GitHub. | Mantenibilidad | **P1 — Alta** |
| **RNF-09** | El procesamiento debe generar reportes y mensajes de error que permitan identificar fallas en los datos o en la ejecución. | Observabilidad | **P1 — Alta** |
| **RNF-10** | La futura API debe utilizar FastAPI, validación de entradas y documentación OpenAPI cuando se implemente en un sprint posterior. | Arquitectura | **P2 — Media** |
| **RNF-11** | La solución web futura debe mantener estricta separación entre presentación, lógica de negocio, datos y componente analítico. | Arquitectura | **P2 — Media** |
| **RNF-12** | Los datos y resultados deben manejarse con controles de acceso adecuados antes de utilizar información industrial real. | Seguridad | **P2 — Media** |
