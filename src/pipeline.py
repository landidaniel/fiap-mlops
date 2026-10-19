"""Pipeline de feature engineering completo."""
import logging
from pathlib import Path

from data.load import load_iris_df
from data.validate import validate_schema, detect_outliers_iqr
from features.build import add_derived_features

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("pipeline")


def run():
    logger.info("🚀 Pipeline de features iniciado")

    # 1. Carregar
    df = load_iris_df()

    # 2. Validar
    validate_schema(df)

    # 3. Detectar outliers (não removemos no Iris, só logamos)
    for col in ["sepal_length", "sepal_width", "petal_length", "petal_width"]:
        detect_outliers_iqr(df, col)

    # 4. Features derivadas
    df = add_derived_features(df)

    # 5. Persistir
    Path("data/processed").mkdir(parents=True, exist_ok=True)
    out = "data/processed/iris_features.csv"
    df.to_csv(out, index=False)
    logger.info(f"💾 Dataset salvo em {out}")

    logger.info(f"🎉 Pipeline concluído. Shape final: {df.shape}")
    return df


if __name__ == "__main__":
    run()