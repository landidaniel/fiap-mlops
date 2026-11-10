"""API de inferencia do modelo Iris.

Esta e a aplicacao que o Kubernetes orquestra (Aula 08, video 82) e que o
pipeline de CI/CD publica como imagem (video 83).

Endpoints:
    GET  /health   -> liveness  (o processo esta de pe?)
    GET  /ready    -> readiness (o modelo carrega? pronto pra receber trafego?)
    GET  /version  -> qual versao/modelo esta servindo (uso em blue-green/canary)
    POST /predict  -> inferencia

Variaveis de ambiente:
    MODEL_PATH   caminho do .pkl (default: models/model.pkl)
    APP_VERSION  rotulo da versao servida (default: dev)
    PORT         porta do servidor de dev (default: 5001)
"""

import os
from pathlib import Path

import joblib
from flask import Flask, jsonify, request

MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/model.pkl"))
APP_VERSION = os.getenv("APP_VERSION", "dev")
CLASSES = ["setosa", "versicolor", "virginica"]

app = Flask(__name__)
_model = None


def get_model():
    """Carrega o modelo uma unica vez (lazy load) e mantem em cache."""
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


@app.get("/health")
def health():
    """Liveness: o processo respondeu, entao esta vivo."""
    return jsonify(status="alive", version=APP_VERSION), 200


@app.get("/ready")
def ready():
    """Readiness: so recebe trafego se o modelo carregar de verdade."""
    try:
        get_model()
    except Exception as exc:  # noqa: BLE001
        return jsonify(status="not-ready", reason=str(exc), version=APP_VERSION), 503
    return jsonify(status="ready", version=APP_VERSION), 200


@app.get("/version")
def version():
    """Versao servida (util para visualizar blue-green / canary)."""
    return jsonify(version=APP_VERSION, model_path=str(MODEL_PATH)), 200


@app.post("/predict")
def predict():
    """Recebe 4 features do Iris e devolve a classe prevista."""
    payload = request.get_json(force=True, silent=True) or {}
    features = payload.get("features")

    if not isinstance(features, list) or len(features) != 4:
        return jsonify(error="envie 'features' como lista de 4 numeros"), 400

    try:
        values = [float(x) for x in features]
    except (TypeError, ValueError):
        return jsonify(error="'features' deve conter apenas numeros"), 400

    pred = int(get_model().predict([values])[0])
    return jsonify(prediction=pred, label=CLASSES[pred], version=APP_VERSION), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5001")))
