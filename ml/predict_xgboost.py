import os

# Allow XGBoost + PyTorch to coexist when this module is imported first.
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")

from dataclasses import dataclass

import numpy as np

from state import AgentState

MODEL_PATH = "models/xgboost_recommendation.pkl"
LABEL_ENCODER_PATH = "models/label_encoder.pkl"
IMPUTER_PATH = "models/feature_imputer.pkl"

FEATURE_COLUMNS = [
    "revenue_growth",
    "net_income",
    "current_ratio",
    "debt_ratio",
    "gross_margin",
    "asset_turnover",
    "altman_z",
    "piotroski_f",
]


@dataclass
class MLPrediction:
    recommendation: str
    confidence: str
    probabilities: dict[str, float]
    features: dict[str, float | None]


def _safe_ratio(
    numerator: float | None,
    denominator: float | None,
) -> float | None:
    if (
        numerator is None
        or denominator is None
        or denominator == 0
    ):
        return None

    return numerator / denominator


def extract_features(
    state: AgentState,
) -> dict[str, float | None]:
    if state.financial_data is None:
        return {column: None for column in FEATURE_COLUMNS}

    current = state.financial_data.current_year
    previous = state.financial_data.previous_year

    revenue = current.revenue
    previous_revenue = previous.revenue

    revenue_growth = None
    if (
        revenue is not None
        and previous_revenue is not None
        and previous_revenue != 0
    ):
        revenue_growth = (
            (revenue - previous_revenue)
            / previous_revenue
        )

    return {
        "revenue_growth": revenue_growth,
        "net_income": current.net_income,
        "current_ratio": _safe_ratio(
            current.current_assets,
            current.current_liabilities,
        ),
        "debt_ratio": _safe_ratio(
            current.total_liabilities,
            current.total_assets,
        ),
        "gross_margin": _safe_ratio(
            current.gross_profit,
            revenue,
        ),
        "asset_turnover": _safe_ratio(
            revenue,
            current.total_assets,
        ),
        "altman_z": (
            state.risk_metrics.altman_z_score
            if state.risk_metrics
            else None
        ),
        "piotroski_f": (
            float(state.risk_metrics.piotroski_f_score)
            if state.risk_metrics
            and state.risk_metrics.piotroski_f_score
            is not None
            else None
        ),
    }


def _confidence_label(
    probabilities: dict[str, float],
    recommendation: str,
) -> str:
    probability = probabilities.get(recommendation, 0.0)

    if probability >= 0.7:
        return "HIGH"
    if probability >= 0.45:
        return "MEDIUM"

    return "LOW"


def predict_recommendation(
    state: AgentState,
    model_path: str = MODEL_PATH,
    label_encoder_path: str = LABEL_ENCODER_PATH,
    imputer_path: str = IMPUTER_PATH,
) -> MLPrediction:
    features = extract_features(state)
    feature_vector = np.array(
        [[features[column] for column in FEATURE_COLUMNS]],
        dtype=float,
    )

    if not all(
        os.path.exists(path)
        for path in (
            model_path,
            label_encoder_path,
            imputer_path,
        )
    ):
        return MLPrediction(
            recommendation="UNAVAILABLE",
            confidence="N/A",
            probabilities={},
            features=features,
        )

    import joblib

    model = joblib.load(model_path)
    label_encoder = joblib.load(label_encoder_path)
    imputer = joblib.load(imputer_path)

    imputed_features = imputer.transform(feature_vector)
    encoded_prediction = model.predict(imputed_features)[0]
    probability_vector = model.predict_proba(
        imputed_features
    )[0]

    recommendation = label_encoder.inverse_transform(
        [encoded_prediction]
    )[0]

    probabilities = {
        str(label): float(probability)
        for label, probability in zip(
            label_encoder.classes_,
            probability_vector,
        )
    }

    return MLPrediction(
        recommendation=recommendation,
        confidence=_confidence_label(
            probabilities,
            recommendation,
        ),
        probabilities=probabilities,
        features=features,
    )
