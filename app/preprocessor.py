import __main__
from pathlib import Path

import joblib

from app.tokenizers import semicolon_tokenizer


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

PREPROCESSOR_PATH = (
    BASE_DIR / "models" / "feature_selection" / "preprocessor.joblib"
)

MODEL_PATH = BASE_DIR / "models" / "sgd_classifier.joblib"


# --------------------------------------------------
# TOKENIZER COMPATIBILITY
# --------------------------------------------------

# The saved preprocessor references the tokenizer
# through __main__.semicolon_tokenizer.

__main__.semicolon_tokenizer = semicolon_tokenizer


# --------------------------------------------------
# LOAD MODEL ARTIFACTS
# --------------------------------------------------

def load_artifacts():

    if not PREPROCESSOR_PATH.exists():
        raise FileNotFoundError(
            f"Preprocessor not found: {PREPROCESSOR_PATH}"
        )

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Model not found: {MODEL_PATH}"
        )

    preprocessor = joblib.load(PREPROCESSOR_PATH)

    classifier = joblib.load(MODEL_PATH)

    print("Preprocessor loaded successfully!")
    print("SGD Classifier loaded successfully!")

    return preprocessor, classifier


# --------------------------------------------------
# FEATURE TRANSFORMATION
# --------------------------------------------------

def transform_features(data, preprocessor):

    import pandas as pd

    df = pd.DataFrame([data])

    expected_features = list(preprocessor.feature_names_in_)

    missing_features = [
        feature
        for feature in expected_features
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing required features: {missing_features}"
        )

    df = df[expected_features]

    return preprocessor.transform(df)

