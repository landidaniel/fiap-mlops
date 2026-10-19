import pytest
import pandas as pd
from data.load import load_iris_df
from data.validate import validate_schema


def test_schema_iris_e_valido():
    df = load_iris_df()
    assert validate_schema(df) is True


def test_schema_coluna_faltando_falha():
    df = load_iris_df().drop(columns=["target"])
    with pytest.raises(AssertionError, match="Colunas faltando"):
        validate_schema(df)


def test_schema_tipo_errado_falha():
    df = load_iris_df()
    df["target"] = df["target"].astype(str)
    with pytest.raises(AssertionError, match="Tipo errado"):
        validate_schema(df)