# telemetry/anomaly.py
from __future__ import annotations

from pathlib import Path
from typing import Tuple, Dict, Any

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

from .config import MODEL_PATH


FEATURE_COLUMNS = [
    "battery_v",
    "panel_i",
    "temp_c",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "mode",
]


def _prepare_features(df: pd.DataFrame) -> np.ndarray:
    x = df[FEATURE_COLUMNS].copy()
    # Mode
    return x.values.astype(float)


def train_anomaly_model(
    df: pd.DataFrame,
    model_path: Path | None = None,
    contamination: float = 0.03,  
) -> Path:
    """
    Train an Isolation Forest on the provided dataframe.
    """
    if model_path is None:
        model_path = MODEL_PATH

    X = _prepare_features(df)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    model.fit(X)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    return model_path


def run_detection(
    df: pd.DataFrame,
    model_path: Path | None = None,
    threshold: float = 0.9,
) -> pd.DataFrame:
    """
    Load trained model and annotate df with anomaly score + flag.

    :param threshold: anomaly_score above this is considered anomalous (0..1, higher = rarer)
    """
    if model_path is None:
        model_path = MODEL_PATH

    model: IsolationForest = joblib.load(model_path)
    X = _prepare_features(df)

    # sklearn IsolationForest
    raw_scores = model.score_samples(X)
    #  anomaly_score in [0, 1], where 1 = most anomalous
    scores = (raw_scores.min() - raw_scores) / (raw_scores.min() - raw_scores.max() + 1e-9)

    df = df.copy()
    df["anomaly_score"] = scores
    df["is_anomaly"] = df["anomaly_score"] > threshold

    return df


def compute_summary_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """Compute simple stats to give to the AI for explanations."""
    stats: Dict[str, Any] = {}
    numeric_cols = FEATURE_COLUMNS
    normal_df = df[~df["is_anomaly"]] if "is_anomaly" in df.columns else df

    for col in numeric_cols:
        series = normal_df[col]
        stats[col] = {
            "mean": float(series.mean()),
            "std": float(series.std()),
            "min": float(series.min()),
            "max": float(series.max()),
        }

    stats["total_packets"] = int(len(df))
    stats["anomaly_count"] = int(df["is_anomaly"].sum() if "is_anomaly" in df.columns else 0)
    return stats
