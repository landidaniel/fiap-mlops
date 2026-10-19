"""Transformações de features."""

import logging

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

logger = logging.getLogger(__name__)


def fit_scaler(X_train):
    """Treina scaler apenas no conjunto de treino."""
    scaler = StandardScaler()
    scaler.fit(X_train)

    logger.info(
        f"Scaler treinado. Médias: {scaler.mean_[:3].round(2)}"
    )

    return scaler


def transform(scaler, X):
    """Aplica o scaler em qualquer conjunto de dados."""
    return scaler.transform(X)


def build_numeric_pipeline():
    """Pipeline: imputação de valores faltantes e normalização."""
    return Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )


def build_full_preprocessor(numeric_cols, categorical_cols):
    """Aplica transformação diferente em cada tipo de coluna."""
    numeric_pipe = build_numeric_pipeline()

    categorical_pipe = Pipeline(
        [
            (
                "encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
            ),
        ]
    )

    return ColumnTransformer(
        [
            ("num", numeric_pipe, numeric_cols),
            ("cat", categorical_pipe, categorical_cols),
        ]
    )
