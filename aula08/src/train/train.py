"""Treina modelo Iris e salva como models/model.pkl."""

from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


def main() -> None:
    X, y = load_iris(return_X_y=True)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_tr, y_tr)

    accuracy = model.score(X_te, y_te)
    print(f"Accuracy: {accuracy:.3f}")

    Path("models").mkdir(exist_ok=True)
    joblib.dump(model, "models/model.pkl")
    print("💾 Modelo salvo em models/model.pkl")


if __name__ == "__main__":
    main()
