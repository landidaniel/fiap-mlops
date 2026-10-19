from data.load import load_iris_df
from features.build import add_derived_features


def test_adiciona_4_features_derivadas():
    df = load_iris_df()
    df_new = add_derived_features(df)

    novas = {"sepal_area", "petal_area", "petal_sepal_length_ratio", "petal_sepal_width_ratio"}
    assert novas.issubset(df_new.columns)
    assert df_new.shape == (150, 9)  # 5 originais + 4 derivadas


def test_petal_area_calculo_correto():
    df = load_iris_df()
    df_new = add_derived_features(df)
    esperado = df.loc[0, "petal_length"] * df.loc[0, "petal_width"]
    assert df_new.loc[0, "petal_area"] == esperado