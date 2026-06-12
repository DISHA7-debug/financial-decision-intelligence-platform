import csv
import os

import joblib
import numpy as np
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_sample_weight
from xgboost import XGBClassifier

DATASET_PATH = (
    "data/datasets/company_features.csv"
)
MODEL_PATH = (
    "models/xgboost_recommendation.pkl"
)
LABEL_ENCODER_PATH = (
    "models/label_encoder.pkl"
)
IMPUTER_PATH = (
    "models/feature_imputer.pkl"
)

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

TARGET_COLUMN = "recommendation"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def _parse_float(
    value: str
) -> float:
    if value is None or value == "":
        return np.nan

    return float(value)


def load_dataset(
    dataset_path: str = DATASET_PATH,
) -> tuple[np.ndarray, np.ndarray, list[str]]:
    feature_rows = []
    labels = []

    with open(dataset_path, newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            recommendation = row.get(TARGET_COLUMN, "").strip()

            if not recommendation:
                continue

            feature_rows.append([
                _parse_float(row.get(column))
                for column in FEATURE_COLUMNS
            ])
            labels.append(recommendation)

    return (
        np.array(feature_rows, dtype=float),
        np.array(labels),
        FEATURE_COLUMNS,
    )


def train_model(
    dataset_path: str = DATASET_PATH,
    model_path: str = MODEL_PATH,
    label_encoder_path: str = LABEL_ENCODER_PATH,
    imputer_path: str = IMPUTER_PATH,
    random_state: int = RANDOM_STATE,
    test_size: float = TEST_SIZE,
) -> dict:
    features, raw_labels, feature_names = (
        load_dataset(dataset_path)
    )

    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(
        raw_labels
    )

    (
        x_train,
        x_test,
        y_train,
        y_test,
    ) = train_test_split(
        features,
        encoded_labels,
        test_size=test_size,
        random_state=random_state,
        stratify=encoded_labels,
    )

    imputer = SimpleImputer(strategy="median")
    x_train = imputer.fit_transform(x_train)
    x_test = imputer.transform(x_test)

    sample_weights = compute_sample_weight(
        class_weight="balanced",
        y=y_train,
    )

    model = XGBClassifier(
        objective="multi:softmax",
        num_class=len(label_encoder.classes_),
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=random_state,
        eval_metric="mlogloss",
    )

    model.fit(
        x_train,
        y_train,
        sample_weight=sample_weights,
    )

    predictions = model.predict(x_test)

    unique, counts = np.unique(
        raw_labels,
        return_counts=True,
    )
    class_distribution = dict(
        zip(unique.tolist(), counts.tolist())
    )

    feature_importance = dict(
        sorted(
            zip(
                feature_names,
                model.feature_importances_,
            ),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    metrics = {
        "accuracy": accuracy_score(
            y_test,
            predictions,
        ),
        "precision": precision_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        ),
        "recall": recall_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        ),
        "f1": f1_score(
            y_test,
            predictions,
            average="weighted",
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(
            y_test,
            predictions,
        ),
        "classification_report": classification_report(
            y_test,
            predictions,
            target_names=label_encoder.classes_,
            zero_division=0,
        ),
        "feature_importance": feature_importance,
    }

    os.makedirs(
        os.path.dirname(model_path),
        exist_ok=True,
    )

    joblib.dump(model, model_path)
    joblib.dump(label_encoder, label_encoder_path)
    joblib.dump(imputer, imputer_path)

    split_summary = {
        "total_rows": len(raw_labels),
        "feature_count": len(feature_names),
        "train_rows": len(y_train),
        "test_rows": len(y_test),
        "class_distribution": class_distribution,
        "encoded_classes": list(
            label_encoder.classes_
        ),
    }

    return {
        "metrics": metrics,
        "split_summary": split_summary,
        "model_path": model_path,
        "label_encoder_path": label_encoder_path,
        "imputer_path": imputer_path,
    }


def print_training_report(
    results: dict
) -> None:
    split_summary = results["split_summary"]
    metrics = results["metrics"]

    print("\n===== XGBOOST TRAINING REPORT =====\n")
    print(
        f"Dataset shape: "
        f"{split_summary['total_rows']} rows x "
        f"{split_summary['feature_count']} features"
    )
    print(
        f"Train rows: {split_summary['train_rows']} | "
        f"Test rows: {split_summary['test_rows']}"
    )
    print(
        f"Class distribution: "
        f"{split_summary['class_distribution']}"
    )
    encoded_labels = [
        str(label)
        for label in split_summary["encoded_classes"]
    ]
    print(f"Encoded labels: {encoded_labels}")

    print("\n--- Metrics (weighted) ---\n")
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")

    print("\n--- Confusion Matrix ---\n")
    print(metrics["confusion_matrix"])
    print("\nRows = actual, Columns = predicted")
    print(f"Label order: {encoded_labels}")

    print("\n--- Classification Report ---\n")
    print(metrics["classification_report"])

    print("\n--- Feature Importance ---\n")

    for rank, (feature, importance) in enumerate(
        metrics["feature_importance"].items(),
        start=1,
    ):
        print(
            f"{rank}. {feature}: {importance:.6f}"
        )

    print("\n--- Saved Artifacts ---\n")
    print(f"Model: {results['model_path']}")
    print(
        f"Label encoder: {results['label_encoder_path']}"
    )
    print(
        f"Feature imputer: {results['imputer_path']}"
    )


if __name__ == "__main__":
    training_results = train_model()
    print_training_report(training_results)
