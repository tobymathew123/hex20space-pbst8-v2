# telemetry/visual_data.py
from __future__ import annotations
from pathlib import Path
import pandas as pd

from .config import DEFAULT_CSV_FILE, MODEL_PATH
from .decoder import decode_bin_to_df
from .anomaly import run_detection


def get_timeseries_for_ui(
    csv_path: Path | None = None,
    model_path: Path | None = None,
    threshold: float = 0.9,
) -> pd.DataFrame:
    """
    Returns a DataFrame ready for plotting:
    timestamp + telemetry values + anomaly score + anomaly flag
    """
    if csv_path is None:
        csv_path = DEFAULT_CSV_FILE

    if Path(csv_path).exists():
        df = pd.read_csv(csv_path)
    else:
        df, _ = decode_bin_to_df()

    df_detected = run_detection(df, model_path=model_path, threshold=threshold)

    
    if "timestamp" in df_detected.columns:
        df_detected["timestamp"] = pd.to_numeric(df_detected["timestamp"], errors="coerce")

    return df_detected


def summarize_for_ui(df: pd.DataFrame) -> dict:
    """
    Lightweight summary for UI cards.
    """
    return {
        "total_packets": int(len(df)),
        "anomaly_count": int(df["is_anomaly"].sum()),
        "first_timestamp": int(df["timestamp"].iloc[0]),
        "last_timestamp": int(df["timestamp"].iloc[-1]),
    }
