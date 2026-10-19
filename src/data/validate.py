"""Validação de qualidade dos dados."""

import logging

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

EXPECTED_SCHEMA = {
    "sepal_length": "float64",
    "sepal_width": "float64",
    "petal_length": "float64",
    "petal_width": "float64",
    "target": "int64",
}


def validate_data(X, y):
    """Valida que os dados estão prontos para treino.

    Args:
        X: Matriz de features.
        y: Vetor de labels.

    Returns:
        bool: True se válido.

    Raises:
        AssertionError: Se alguma validação falhar.
    """
    logger.info("Validando dados...")

    assert len(X) > 0, "Dataset vazio!"
    assert len(X) == len(y), "X e y com tamanhos diferentes!"
    assert not np.isnan(X).any(), "X contém NaN!"
    assert len(np.unique(y)) >= 2, "Menos de 2 classes!"

    logger.info(
        f"✅ Dados válidos: {len(X)} amostras, "
        f"{len(np.unique(y))} classes"
    )

    return True


def validate_schema(df: pd.DataFrame) -> bool:
    """Valida colunas e tipos."""
    logger.info("Validando schema...")

    # 1. Verifica se existem colunas obrigatórias
    missing = set(EXPECTED_SCHEMA) - set(df.columns)

    assert not missing, f"Colunas faltando: {missing}"

    # 2. Verifica os tipos das colunas
    for col, expected_type in EXPECTED_SCHEMA.items():
        actual_type = str(df[col].dtype)

        assert actual_type == expected_type, (
            f"Tipo errado em '{col}': "
            f"esperado {expected_type}, obtido {actual_type}"
        )

    logger.info(
        f"✅ Schema válido: {len(df)} linhas x "
        f"{len(df.columns)} colunas"
    )

    return True


def detect_outliers_iqr(
    df: pd.DataFrame,
    column: str,
) -> pd.DataFrame:
    """Detecta outliers usando IQR (Interquartile Range)."""
    q1 = df[column].quantile(0.25)
    q3 = df[column].quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    outliers = df[
        (df[column] < lower) | (df[column] > upper)
    ]

    logger.info(
        f"Outliers em '{column}': "
        f"{len(outliers)} / {len(df)}"
    )

    return outliers
