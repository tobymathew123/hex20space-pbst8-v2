# telemetry/inspection.py
from __future__ import annotations

from typing import Dict, Any
from pathlib import Path

import pandas as pd

from .config import DEFAULT_CSV_FILE, MODEL_PATH
from .decoder import decode_bin_to_df
from .anomaly import run_detection, compute_summary_stats, FEATURE_COLUMNS
from .ai import explain_anomaly as ai_explain_anomaly


def _load_or_decode(csv_path: Path | None = None) -> pd.DataFrame:
    """
    Load telemetry from CSV if it exists, otherwise decode from the latest .bin.
    """
    if csv_path is None:
        csv_path = DEFAULT_CSV_FILE

    if Path(csv_path).exists():
        return pd.read_csv(csv_path)

    # decode from bin 
    df, _ = decode_bin_to_df()
    return df


def explain_top_anomaly(
    csv_path: Path | None = None,
    model_path: Path | None = None,
    threshold: float = 0.9,
) -> Dict[str, Any]:
    """
    Find the most anomalous packet and ask the AI to explain it.

    Returns a dict with:
      - packet_index
      - anomaly_score
      - packet (features only)
      - explanation (bullet points text)
      - message (if no anomalies)
    """
    if model_path is None:
        model_path = MODEL_PATH

    df = _load_or_decode(csv_path)

    # Run detection 
    try:
        df_detected = run_detection(df, model_path=model_path, threshold=threshold)
    except FileNotFoundError:
        # Model not trained 
        from .anomaly import train_anomaly_model

        train_anomaly_model(df, model_path=model_path)
        df_detected = run_detection(df, model_path=model_path, threshold=threshold)

    if "is_anomaly" not in df_detected.columns or not df_detected["is_anomaly"].any():
        return {
            "message": "No anomalies detected in the current dataset.",
        }

    # most anomalous packet (highest anomaly_score)
    df_anom = df_detected[df_detected["is_anomaly"]].copy()
    top_row = df_anom.sort_values("anomaly_score", ascending=False).iloc[0]

    stats = compute_summary_stats(df_detected)

    packet = {col: float(top_row[col]) for col in FEATURE_COLUMNS}
    anomaly_score = float(top_row["anomaly_score"])

    explanation_text = ai_explain_anomaly(packet, stats, anomaly_score)

    return {
        "packet_index": int(top_row.name),
        "anomaly_score": anomaly_score,
        "packet": packet,
        "explanation": explanation_text,
    }
