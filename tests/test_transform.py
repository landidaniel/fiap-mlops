import pandas as pd
from features.transform import build_full_preprocessor


def test_pipeline_processa_dataframe_misto():
    df = pd.DataFrame({
        "idade": [25, 45, 35],
        "salario": [3000, 8000, 5000],
        "cidade": ["SP", "RJ", "MG"],
    })

    preprocessor = build_full_preprocessor(
        numeric_cols=["idade", "salario"],
        categorical_cols=["cidade"],
    )

    X = preprocessor.fit_transform(df)

    # 2 numéricas + 3 cidades = 5 colunas
    assert X.shape == (3, 5)