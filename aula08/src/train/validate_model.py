"""Valida modelo treinado contra threshold mínimo.

Saída com código != 0 se modelo for inaceitável.
Este é o ponto que TRAVA o CI quando a qualidade cai.
"""

import sys
from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

MIN_ACCURACY = 0.85


def main() -> None:
    model_path = Path("models/model.pkl")
    if not model_path.exists():
        print(f"❌ Modelo não encontrado: {model_path}")
        sys.exit(1)

    model = joblib.load(model_path)
    X, y = load_iris(return_X_y=True)
    _, X_te, _, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    accuracy = float(accuracy_score(y_te, model.predict(X_te)))
    print(f"Accuracy: {accuracy:.3f} | Threshold: {MIN_ACCURACY}")

    if accuracy < MIN_ACCURACY:
        print(f"❌ Modelo abaixo do threshold ({MIN_ACCURACY})")
        sys.exit(1)

    print("✅ Modelo aprovado")


if __name__ == "__main__":
    main()
