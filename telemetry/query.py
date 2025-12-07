# telemetry/query.py
from __future__ import annotations

from typing import Dict, Any

import pandas as pd

from .visual_data import get_timeseries_for_ui, summarize_for_ui
from .anomaly import FEATURE_COLUMNS
from .ai import answer_telemetry_question as ai_answer_telemetry_question


def _build_schema(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Build a simple schema description for the AI:
      - column names
      - dtypes
    """
    schema = {
        "columns": [],
    }
    for col in df.columns:
        schema["columns"].append(
            {
                "name": col,
                "dtype": str(df[col].dtype),
            }
        )
    return schema


def _build_context(df: pd.DataFrame) -> str:
    """
    Build a compact text context summary for the AI:
      - total packets
      - anomaly count
      - per-feature min / max / mean (for main features)
    """
    summary = summarize_for_ui(df)
    lines = []

    lines.append(
        f"Total packets: {summary.get('total_packets', len(df))}, "
        f"anomalies: {summary.get('anomaly_count', int(df['is_anomaly'].sum()))}."
    )

    lines.append("Per-feature statistics (for main telemetry fields):")
    for col in FEATURE_COLUMNS:
        series = df[col]
        lines.append(
            f"  {col}: min={series.min():.3f}, max={series.max():.3f}, "
            f"mean={series.mean():.3f}, std={series.std():.3f}"
        )

    return "\n".join(lines)


def ask_telemetry(question: str) -> Dict[str, Any]:
    """
    High-level backend API:
    - loads latest telemetry
    - computes schema + context
    - asks AI to answer the question
    """
    df = get_timeseries_for_ui()
    schema = _build_schema(df)
    context = _build_context(df)

    answer_text = ai_answer_telemetry_question(
        question=question,
        df_schema=schema,
        context=context,
    )

    return {
        "question": question,
        "answer": answer_text,
        "schema": schema,
        "context_preview": context[:500],  
    }
