"""Tests for FastAPI /predict and /health over modelo.joblib."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import main as ml_main


@pytest.fixture()
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    model_src = Path(__file__).resolve().parents[1] / "artifacts" / "modelo.joblib"
    if not model_src.is_file():
        pytest.skip("modelo.joblib is required for predict API tests")

    target = tmp_path / "modelo.joblib"
    target.write_bytes(model_src.read_bytes())
    monkeypatch.setattr(ml_main, "MODEL_PATH", target)
    ml_main._clear_model_cache()
    return TestClient(ml_main.app)


def test_health_ok_when_model_present(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["model_loaded"] is True
    assert body["status"] == "ok"


def test_predict_returns_probability_in_unit_interval(client: TestClient) -> None:
    response = client.post(
        "/predict",
        json={
            "air_temperature_k": 298.1,
            "process_temperature_k": 308.6,
            "rotational_speed_rpm": 1551,
            "torque_nm": 42.8,
            "tool_wear_min": 0,
            "product_type": "M",
        },
    )
    assert response.status_code == 200
    probability = response.json()["failure_probability"]
    assert isinstance(probability, float)
    assert 0.0 <= probability <= 1.0


def test_predict_missing_model_returns_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing = tmp_path / "missing.joblib"
    monkeypatch.setattr(ml_main, "MODEL_PATH", missing)
    ml_main._clear_model_cache()
    client = TestClient(ml_main.app)
    response = client.post(
        "/predict",
        json={
            "air_temperature_k": 298.1,
            "process_temperature_k": 308.6,
            "rotational_speed_rpm": 1551,
            "torque_nm": 42.8,
            "tool_wear_min": 0,
            "product_type": "M",
        },
    )
    assert response.status_code == 503
