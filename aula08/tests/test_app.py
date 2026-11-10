"""Testes da API de inferencia (src/serve/app.py)."""

import subprocess
import sys

import pytest

from src.serve import app as app_module


@pytest.fixture(scope="module", autouse=True)
def _ensure_model():
    """Garante que o modelo existe antes de exercitar a API."""
    subprocess.run([sys.executable, "src/train/train.py"], check=True)
    # zera o cache para o teste carregar o .pkl recem gerado
    app_module._model = None


@pytest.fixture()
def client():
    app_module.app.config.update(TESTING=True)
    return app_module.app.test_client()


def test_health_responde_alive(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "alive"


def test_ready_carrega_modelo(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ready"


def test_predict_retorna_classe_valida(client):
    resp = client.post("/predict", json={"features": [5.1, 3.5, 1.4, 0.2]})
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["prediction"] in [0, 1, 2]
    assert body["label"] in ["setosa", "versicolor", "virginica"]


def test_predict_rejeita_payload_invalido(client):
    resp = client.post("/predict", json={"features": [1.0, 2.0]})
    assert resp.status_code == 400
