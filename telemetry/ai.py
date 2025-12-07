# telemetry/ai.py
from __future__ import annotations

from typing import Dict, Any

from openai import OpenAI

from .config import OPENAI_API_KEY, OPENAI_MODEL

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        if not OPENAI_API_KEY:
            raise RuntimeError("OPENAI_API_KEY is not set in environment or .env.")
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client


def _chat(system: str, user: str) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()


def create_nightly_briefing(run_summary: Dict[str, Any]) -> str:
    """
    Create a concise mission briefing in bullet-point format.
    """
    system = (
        "You are a mission operations engineer for a CubeSat. "
        "Summarize nightly telemetry anomaly detection runs in clear, concise language."
    )
    user = (
        "Here is the summary of the nightly run as JSON-like data:\n"
        f"{run_summary}\n\n"
        "Write a mission briefing in bullet-point format. Use 4–7 bullets, each starting with '- '. "
        "Include:\n"
        "- How many packets were processed\n"
        "- How many anomalies were found\n"
        "- Which subsystems look problematic (power, thermal, attitude)\n"
        "- Any trends that might deserve investigation\n"
        "Be factual, not dramatic, and do not add extra headings."
    )
    return _chat(system, user)


def create_briefing_actions(run_summary: Dict[str, Any], briefing: str) -> str:
    """
    Turn the briefing + stats into bullet-point findings and recommended checks.
    """
    system = (
        "You are a senior satellite operations engineer helping to create a nightly report. "
        "Based on the mission briefing and run statistics, you will extract key findings and "
        "recommend concrete checks or follow-up actions for the engineering team."
    )
    user = (
        "Here is the JSON-like summary of the nightly run:\n"
        f"{run_summary}\n\n"
        "Here is the AI mission briefing that was already generated:\n"
        f"{briefing}\n\n"
        "Produce two sections in plain text:\n"
        "1) 'Key Findings:' followed by 3–6 bullet points starting with '- '.\n"
        "2) 'Recommended Checks / Actions:' followed by 3–6 bullet points starting with '- '.\n"
        "Keep each bullet short and specific. Do not add any extra headings beyond those two."
    )
    return _chat(system, user)


def explain_anomaly(
    packet: Dict[str, Any],
    stats: Dict[str, Any],
    anomaly_score: float,
) -> str:
    system = (
        "You are a satellite health monitoring expert. "
        "Explain anomalies in CubeSat telemetry to engineers."
    )
    user = (
        "We have an anomalous telemetry packet with fields:\n"
        f"{packet}\n\n"
        "Normal baseline statistics for each field are:\n"
        f"{stats}\n\n"
        f"This packet's anomaly score from an Isolation Forest model is {anomaly_score:.3f} "
        "(where higher means more anomalous).\n"
        "Explain in 3–5 bullet points why this packet might be anomalous and which subsystem(s) "
        "could be affected. Use short, clear sentences."
    )
    return _chat(system, user)


def answer_telemetry_question(
    question: str,
    df_schema: Dict[str, Any],
    context: str,
) -> str:
    system = (
        "You are assisting with telemetry analysis for a CubeSat. "
        "You will receive the schema of a pandas DataFrame and some context, "
        "then a natural language question. Answer based on that information."
    )
    user = (
        f"DataFrame schema and example meta-data:\n{df_schema}\n\n"
        f"Context summary:\n{context}\n\n"
        f"Question:\n{question}\n\n"
        "Answer concisely and, if needed, suggest what plots or filters could help investigate."
    )
    return _chat(system, user)
