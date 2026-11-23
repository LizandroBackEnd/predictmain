"""FastAPI inference entrypoint for PredictMain HU-08 baseline model."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sklearn.pipeline import Pipeline

ARTIFACTS_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_PATH = ARTIFACTS_DIR / "modelo.joblib"

app = FastAPI(title="PredictMain ML Inference", version="1.0.0")


class PredictRequest(BaseModel):
    """Raw sensor features matching the HU-06/HU-08 training frame."""

    model_config = ConfigDict(extra="forbid")

    air_temperature_k: float = Field(..., description="Air temperature [K]")
    process_temperature_k: float = Field(..., description="Process temperature [K]")
    rotational_speed_rpm: float = Field(..., description="Rotational speed [rpm]")
    torque_nm: float = Field(..., description="Torque [Nm]")
    tool_wear_min: float = Field(..., description="Tool wear [min]")
    product_type: Literal["L", "M", "H"] = Field(..., description="Product Type")


class PredictResponse(BaseModel):
    failure_probability: float


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    model_loaded: bool
    model_path: str


@lru_cache(maxsize=1)
def _load_model() -> Pipeline:
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model artifact not found: {MODEL_PATH}")
    model = joblib.load(MODEL_PATH)
    if not isinstance(model, Pipeline):
        raise TypeError("modelo.joblib must be a sklearn Pipeline")
    return model


def _clear_model_cache() -> None:
    _load_model.cache_clear()


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    loaded = MODEL_PATH.is_file()
    if loaded:
        try:
            _load_model()
        except Exception:
            loaded = False
    return HealthResponse(
        status="ok" if loaded else "degraded",
        model_loaded=loaded,
        model_path=str(MODEL_PATH),
    )


@app.post("/predict", response_model=PredictResponse)
def predict(body: PredictRequest) -> PredictResponse:
    try:
        model = _load_model()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 — surface load errors to client
        raise HTTPException(status_code=500, detail=f"Failed to load model: {exc}") from exc

    frame = pd.DataFrame(
        [
            {
                "Air temperature [K]": body.air_temperature_k,
                "Process temperature [K]": body.process_temperature_k,
                "Rotational speed [rpm]": body.rotational_speed_rpm,
                "Torque [Nm]": body.torque_nm,
                "Tool wear [min]": body.tool_wear_min,
                "Type": body.product_type,
            }
        ]
    )

    try:
        if not hasattr(model, "predict_proba"):
            raise ValueError("Loaded model does not expose predict_proba")
        proba = model.predict_proba(frame)
        failure_probability = float(proba[0][1])
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Prediction failed: {exc}") from exc

    if not 0.0 <= failure_probability <= 1.0:
        raise HTTPException(status_code=500, detail="Model returned out-of-range probability")

    return PredictResponse(failure_probability=failure_probability)
