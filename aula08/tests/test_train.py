"""Testes do treinamento."""

import subprocess
import sys
from pathlib import Path

import joblib


def test_train_script_roda():
    result = subprocess.run(
        [sys.executable, "src/train/train.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    assert "Accuracy" in result.stdout


def test_modelo_persistido():
    subprocess.run([sys.executable, "src/train/train.py"], check=True)
    assert Path("models/model.pkl").exists()


def test_modelo_faz_predicao():
    subprocess.run([sys.executable, "src/train/train.py"], check=True)
    model = joblib.load("models/model.pkl")
    pred = model.predict([[5.1, 3.5, 1.4, 0.2]])
    assert pred[0] in [0, 1, 2]


def test_validate_model_aprova_modelo_bom():
    subprocess.run([sys.executable, "src/train/train.py"], check=True)
    result = subprocess.run(
        [sys.executable, "src/train/validate_model.py"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "aprovado" in result.stdout
