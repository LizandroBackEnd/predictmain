"""Evaluación del comportamiento inicial del servicio de inferencia.

Ejecuta 13 casos sobre el artefacto real modelo.joblib. No hay agente LLM: la
"respuesta" es la salida determinista de POST /predict o un rechazo HTTP real
del contrato. Escribe la tabla y las métricas en entrega_sprint2/evidencias/.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import HTTPException
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ml_service"))
sys.stdout.reconfigure(encoding="utf-8")

import main as ml_main  # noqa: E402

EVIDENCIAS = ROOT / "entrega_sprint2" / "evidencias"
UMBRAL = 0.5


def _leer_filas() -> dict[int, dict[str, Any]]:
    """Carga el CSV crudo indexado por UDI para citar evidencia real."""
    crudo = pd.read_csv(ROOT / "data" / "raw" / "ai4i2020.csv")
    return {int(row["UDI"]): row for _, row in crudo.iterrows()}


def _payload(fila: dict[str, Any]) -> dict[str, Any]:
    """Traduce columnas AI4I al esquema snake_case de PredictRequest."""
    return {
        "air_temperature_k": float(fila["Air temperature [K]"]),
        "process_temperature_k": float(fila["Process temperature [K]"]),
        "rotational_speed_rpm": float(fila["Rotational speed [rpm]"]),
        "torque_nm": float(fila["Torque [Nm]"]),
        "tool_wear_min": float(fila["Tool wear [min]"]),
        "product_type": str(fila["Type"]),
    }


CASOS: list[dict[str, Any]] = [
    {
        "id": 1, "nivel": "Fácil", "udi": 1,
        "consulta": "Evaluar UDI 1: telemetría nominal, Type M, sin falla registrada.",
        "evidencia": "Fila UDI 1 de ai4i2020.csv; Machine failure=0",
        "esperado": "Probabilidad < 0.30, coherente con la etiqueta.",
        "observacion": "Salida determinista. No hay generación de lenguaje ni citas.",
    },
    {
        "id": 2, "nivel": "Fácil", "udi": 51,
        "consulta": "Evaluar UDI 51: 2861 rpm con torque 4.6 Nm, Type L.",
        "evidencia": "Fila UDI 51; PWF=1; reporte HU-05: RPM>1895.5 es failure_signal",
        "esperado": "Probabilidad > 0.70; coincide con falla etiquetada.",
        "observacion": "Recuperación directa. El extremo de RPM se conservó en HU-05.",
    },
    {
        "id": 3, "nivel": "Fácil", "udi": 70,
        "consulta": "Evaluar UDI 70: torque 65.7 Nm, desgaste 191 min, Type L.",
        "evidencia": "Fila UDI 70; PWF=1 y OSF=1; torque 65.7 Nm > P99=62.8 Nm (HU-05)",
        "esperado": "Probabilidad > 0.70; coincide con falla etiquetada.",
        "observacion": "El torque alto aporta señal; el modelo devuelve probabilidad saturada.",
    },
    {
        "id": 4, "nivel": "Media", "udi": 5402,
        "consulta": "Evaluar UDI 5402: desgaste máximo del dataset, 253 min, Type M.",
        "evidencia": "Fila UDI 5402; reporte HU-05: P99 desgaste=222 min; HU-06 Temp_diff=9.7 K",
        "esperado": "Probabilidad > 0.70; patrón de TWF por desgaste extremo.",
        "observacion": "Combina fila, regla HU-05 y variable derivada. Sin ambigüedad.",
    },
    {
        "id": 5, "nivel": "Media", "udi": 575,
        "consulta": "Evaluar UDI 575: delta de temperatura 12.1 K, sin falla etiquetada.",
        "evidencia": "Fila UDI 575; HU-06 Temp_diff=Process-Air; reporte HU-05 rango proceso 305.7-313.8 K",
        "esperado": "Delta alto por fricción, pero probabilidad < 0.30 según la etiqueta.",
        "observacion": "Temp_diff por sí solo no dispara falla; torque 41.7 Nm está en rango normal.",
    },
    {
        "id": 6, "nivel": "Media", "udi": 995,
        "consulta": "Evaluar UDI 995: 1168 rpm, torque 63.4 Nm, sin falla etiquetada.",
        "evidencia": "Fila UDI 995; RPM 1168=mínimo UCI; torque 63.4 dentro del fence IQR 12.8-67.2",
        "esperado": "Probabilidad < 0.30 a pesar de estar en el borde físico inferior.",
        "observacion": "El caso mezcla dos extremos válidos; el modelo no los trata como error.",
    },
    {
        "id": 7, "nivel": "Media", "udi": 418,
        "consulta": "Evaluar UDI 418: desgaste 213 min, sin falla etiquetada.",
        "evidencia": "Fila UDI 418; desgaste 213 min < P99=222 min; precision global=0.7901",
        "esperado": "Zona limítrofe: probabilidad cercana o superior a 0.50 sin etiqueta de falla.",
        "observacion": "Falso positivo real. Con umbral 0.50 se dispara una alarma no confirmada.",
    },
    {
        "id": 8, "nivel": "Difícil", "udi": 443,
        "consulta": "Evaluar UDI 443: torque 61.5 Nm y desgaste 61 min, falla etiquetada.",
        "evidencia": "Fila UDI 443; PWF=1; torque 61.5 Nm en cola alta (P99=62.8); recall=0.7529",
        "esperado": "Detectar la falla; si la probabilidad es < 0.50 el caso es un falso negativo.",
        "observacion": "Falso negativo real: el umbral 0.50 deja pasar una falla etiquetada.",
    },
    {
        "id": 9, "nivel": "Difícil", "udi": 2865,
        "consulta": "Evaluar UDI 2865: desgaste 246 min, Type H, falla etiquetada.",
        "evidencia": "Fila UDI 2865; HU-06 Type_H es categoría de referencia del One-Hot; P99 desgaste=222 min",
        "esperado": "Riesgo alto por desgaste; verificar si el límite de riesgo medio (0.30) basta.",
        "observacion": "Caso límite: probabilidad en 0.30 y etiqueta 1. Sin ajuste de umbral no se discrimina.",
    },
    {
        "id": 10, "nivel": "Difícil", "modo": "validacion",
        "payload": {"air_temperature_k": 298.1, "process_temperature_k": 308.6,
                    "rotational_speed_rpm": 1551, "torque_nm": 42.8},
        "consulta": "Consultar riesgo de una máquina sin desgaste ni tipo de producto.",
        "evidencia": "Ninguna: el esquema de main.py exige seis campos",
        "esperado": "Rechazo HTTP 422 por campos obligatorios ausentes.",
        "observacion": "Sin telemetría completa no se invoca al modelo. No se inventan valores.",
    },
    {
        "id": 11, "nivel": "Difícil", "modo": "validacion",
        "payload": {"air_temperature_k": 298.1, "process_temperature_k": 308.6,
                    "rotational_speed_rpm": 1551, "torque_nm": 42.8,
                    "tool_wear_min": 0, "product_type": "X"},
        "consulta": "Consultar riesgo con tipo de producto 'X', fuera del catálogo L/M/H.",
        "evidencia": "Ninguna: Literal['L','M','H'] en PredictRequest",
        "esperado": "Rechazo HTTP 422 por valor de Product ID inválido.",
        "observacion": "El catálogo del dataset solo contiene L, M y H. No se normaliza 'X'.",
    },
    {
        "id": 12, "nivel": "Difícil", "modo": "validacion",
        "payload": {"air_temperature_k": 298.1, "process_temperature_k": 308.6,
                    "rotational_speed_rpm": 1551, "torque_nm": 42.8,
                    "tool_wear_min": 0, "product_type": "M", "machine_id": "M14860"},
        "consulta": "Consultar riesgo incluyendo machine_id como campo adicional.",
        "evidencia": "Ninguna: ConfigDict(extra='forbid') en main.py",
        "esperado": "Rechazo HTTP 422 por campo extra.",
        "observacion": "UDI/Product ID están excluidos del modelo (HU-06); el contrato los rechaza.",
    },
    {
        "id": 13, "nivel": "Difícil", "modo": "sin_modelo", "udi": 1,
        "consulta": "Consultar riesgo cuando falta modelo.joblib en el servidor.",
        "evidencia": "Ruta de artifact sustituida por una inexistente en el proceso de prueba",
        "esperado": "HTTP 503, no una probabilidad estimada.",
        "observacion": "Falla de dependencia declarada. El servicio no degrada a una respuesta inventada.",
    },
]


def _calificar(probabilidad: float, etiqueta: int | None) -> str:
    """Calificación contra umbral fijo 0.50; sin ajuste de umbral en HU-08."""
    if etiqueta is None:
        return "✓" if 0.0 <= probabilidad <= 1.0 else "✗"
    predicho = int(probabilidad >= UMBRAL)
    if predicho != etiqueta:
        return "✗"
    if (etiqueta == 1 and probabilidad >= 0.70) or (etiqueta == 0 and probabilidad < 0.30):
        return "✓"
    return "parcial"


def _ejecutar(caso: dict[str, Any], filas: dict[int, dict[str, Any]]) -> dict[str, Any]:
    fila = filas.get(caso.get("udi", -1))
    if caso.get("modo") == "validacion":
        try:
            ml_main.PredictRequest(**caso["payload"])
        except ValidationError as exc:
            mensaje = str(exc.errors()[0].get("msg", "validación fallida"))
            respuesta, resultado = f"HTTP 422: {mensaje}", "✓"
        else:
            respuesta, resultado = "Aceptado por el esquema", "✗"
        return {**caso, "respuesta": respuesta, "resultado": resultado, "probabilidad": None}

    if caso.get("modo") == "sin_modelo":
        original = ml_main.MODEL_PATH
        ml_main.MODEL_PATH = EVIDENCIAS / "modelo_inexistente.joblib"
        ml_main._clear_model_cache()
        try:
            ml_main.predict(ml_main.PredictRequest(**_payload(fila)))
        except HTTPException as exc:
            detalle = "Model artifact not found" if exc.status_code == 503 else str(exc.detail)[:60]
            respuesta = f"HTTP {exc.status_code}: {detalle}"
            resultado = "✓" if exc.status_code == 503 else "✗"
        else:
            respuesta, resultado = "Probabilidad devuelta sin artefacto", "✗"
        finally:
            ml_main.MODEL_PATH = original
            ml_main._clear_model_cache()
        return {**caso, "respuesta": respuesta, "resultado": resultado, "probabilidad": None}

    body = ml_main.PredictRequest(**_payload(fila))
    probabilidad = float(ml_main.predict(body).failure_probability)
    etiqueta = int(fila["Machine failure"])
    return {
        **caso,
        "respuesta": f"failure_probability={probabilidad:.6f}",
        "resultado": _calificar(probabilidad, etiqueta),
        "probabilidad": probabilidad,
    }


def _latencia_ms(body: ml_main.PredictRequest, repeticiones: int = 20) -> float:
    inicio = time.perf_counter()
    for _ in range(repeticiones):
        ml_main.predict(body)
    return (time.perf_counter() - inicio) / repeticiones * 1000


def main() -> int:
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    filas = _leer_filas()
    ejecutados = [_ejecutar(caso, filas) for caso in CASOS]
    cuerpo = [
        "# Resultados de pruebas de inferencia — Sprint 2",
        "",
        "| # | Consulta | Respuesta del agente | Info recuperada (chunk/doc) | Respuesta esperada | Resultado | Observación |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for caso in ejecutados:
        cuerpo.append(
            f"| {caso['id']} | {caso['consulta']} | {caso['respuesta']} | "
            f"{caso['evidencia']} | {caso['esperado']} | {caso['resultado']} | "
            f"{caso['observacion']} |"
        )

    latencia = _latencia_ms(ml_main.PredictRequest(**_payload(filas[1])))
    exitos = sum(1 for caso in ejecutados if caso["resultado"] == "✓")
    parciales = sum(1 for caso in ejecutados if caso["resultado"] == "parcial")
    fallos = sum(1 for caso in ejecutados if caso["resultado"] == "✗")
    cuerpo += [
        "",
        f"Latencia media de inferencia: {latencia:.3f} ms sobre 20 ejecuciones.",
        f"Distribución: {exitos} correctos, {parciales} parciales, {fallos} fallidos.",
        "",
    ]
    (EVIDENCIAS / "tabla_resultados.md").write_text("\n".join(cuerpo), encoding="utf-8")
    metricas = {
        "casos": len(ejecutados), "correctos": exitos, "parciales": parciales,
        "fallidos": fallos, "latencia_media_ms": round(latencia, 3),
        "detalle": [
            {"id": c["id"], "probabilidad": c["probabilidad"], "resultado": c["resultado"]}
            for c in ejecutados
        ],
    }
    (EVIDENCIAS / "metricas_inferencia.json").write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("\n".join(cuerpo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
