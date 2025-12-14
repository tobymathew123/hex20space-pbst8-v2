# telemetry/nightly_job.py
from __future__ import annotations
import json

from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Any

from textwrap import wrap
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .config import (
    DEFAULT_BIN_FILE,
    DEFAULT_CSV_FILE,
    MODEL_PATH,
    REPORTS_DIR,
    NIGHTLY_LOG,
)
from .generator import generate_packets
from .decoder import decode_bin_to_df
from .anomaly import train_anomaly_model, run_detection, compute_summary_stats
from .ai import create_nightly_briefing, create_briefing_actions
from .tts import speak


IST = timezone(timedelta(hours=5, minutes=30))
LAST_SCHEDULED_FILE = Path("data/last_scheduled_run.json")


def _draw_wrapped_text(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    max_width: int,
    line_height: int,
) -> float:
    """
    Draw wrapped text and return the final y position.
    """
    lines = []
    for line in text.splitlines():
        if not line.strip():
            lines.append("")  # blank line
            continue
        lines.extend(wrap(line, max_width))

    for line in lines:
        if y < 60:  
            c.showPage()
            y = c._pagesize[1] - 50
            c.setFont("Helvetica", 10)
        if line:
            c.drawString(x, y, line)
        y -= line_height
    return y


def _create_pdf_report(
    run_summary: Dict[str, Any],
    briefing: str,
    actions_text: str,
    pdf_path: Path,
) -> None:
    """Create a structured PDF report with key numbers, briefing, and actions."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, y, "Nightly Telemetry Report")
    y -= 30

    # Meta info 
    c.setFont("Helvetica", 10)
    c.drawString(margin, y, f"Timestamp (IST): {run_summary['timestamp_readable']}")
    y -= 15
    c.drawString(margin, y, f"Total packets: {run_summary['total_packets']}")
    y -= 15
    c.drawString(margin, y, f"Anomalies detected: {run_summary['anomaly_count']}")
    y -= 15
    c.drawString(margin, y, f"Anomaly rate: {run_summary['anomaly_rate_percent']:.1f}%")
    y -= 20

    # Key numbers section
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Key Numbers")
    y -= 18
    c.setFont("Helvetica", 10)

    stats = run_summary.get("stats", {})
    for key, label in [
        ("battery_v", "Battery voltage (V)"),
        ("panel_i", "Panel current (A)"),
        ("temp_c", "Temperature (°C)"),
    ]:
        if key in stats:
            s = stats[key]
            line = (
                f"- {label}: min={s['min']:.2f}, max={s['max']:.2f}, "
                f"mean={s['mean']:.2f}, std={s['std']:.2f}"
            )
            c.drawString(margin, y, line)
            y -= 14
    y -= 10

    # AI Mission Briefing
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "AI Mission Briefing")
    y -= 18
    c.setFont("Helvetica", 10)
    y = _draw_wrapped_text(c, briefing, margin, y, max_width=100, line_height=14)

    # New page for findings/actions
    c.showPage()
    y = height - margin

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, "Key Findings & Recommended Checks")
    y -= 20
    c.setFont("Helvetica", 10)
    y = _draw_wrapped_text(c, actions_text, margin, y, max_width=100, line_height=14)

    c.showPage()
    c.save()


def run_nightly_job(
    n_packets: int = 500,
    bin_path: Path | None = None,
    csv_path: Path | None = None,
    model_path: Path | None = None,
    use_tts: bool = True,
) -> Dict[str, Any]:
    """
    Full pipeline: generate -> decode -> train (on subset) -> detect -> AI briefing.
    Returns a dict summary for logging / UI.
    """
    if bin_path is None:
        bin_path = DEFAULT_BIN_FILE
    if csv_path is None:
        csv_path = DEFAULT_CSV_FILE
    if model_path is None:
        model_path = MODEL_PATH

    # 1. Generate packets
    bin_path = generate_packets(n_packets=n_packets, out_path=bin_path)

    # 2. Decode all packets
    df, _ = decode_bin_to_df(bin_path=bin_path, save_csv=True, csv_path=csv_path)

    # 3. Train on a subset 
    train_df = df.sample(frac=0.6, random_state=42)  
    model_path = train_anomaly_model(train_df, model_path=model_path, contamination=0.03)

    # 4. Run detection 
    df_detected = run_detection(df, model_path=model_path, threshold=0.9)

    # 5. Compute stats
    stats = compute_summary_stats(df_detected)

    # 6. Build run_summary
    now_ist = datetime.now(IST)
    timestamp_iso = now_ist.isoformat()
    timestamp_readable = now_ist.strftime("%Y-%m-%d %H:%M:%S IST")
    total_packets = int(len(df_detected))
    anomaly_count = stats.get("anomaly_count", int(df_detected["is_anomaly"].sum()))
    anomaly_rate = (anomaly_count / total_packets * 100.0) if total_packets > 0 else 0.0

    run_summary: Dict[str, Any] = {
        "timestamp": timestamp_iso,
        "timestamp_readable": timestamp_readable,
        "total_packets": total_packets,
        "anomaly_count": anomaly_count,
        "anomaly_rate_percent": anomaly_rate,
        "bin_file": str(bin_path),
        "csv_file": str(csv_path),
        "model_path": str(model_path),
        "stats": stats,
    }

    # 7. AI Nightly Mission Briefing
    briefing = create_nightly_briefing(run_summary)
    run_summary["briefing"] = briefing

    # 8. AI Key Findings + Recommended Checks 
    actions_text = create_briefing_actions(run_summary, briefing)
    run_summary["actions"] = actions_text

    # 9. Save PDF report 
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    base_name = f"nightly_{now_ist.strftime('%Y%m%d_%H%M%S')}"
    report_pdf = REPORTS_DIR / f"{base_name}.pdf"
    _create_pdf_report(run_summary, briefing, actions_text, report_pdf)
    run_summary["report_pdf"] = str(report_pdf)

    # 10. Log to text log
    NIGHTLY_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(NIGHTLY_LOG, "a", encoding="utf-8") as log_f:
        log_f.write(
            f"{timestamp_readable} | packets={total_packets}"
            f" anomalies={anomaly_count} | pdf={report_pdf.name}\n"
        )

    # 11. TTS alert/briefing 
    if use_tts:
        if anomaly_count > 0:
            short_alert = (
                f"Nightly run complete. {anomaly_count} anomalies detected "
                f"out of {total_packets} packets."
            )
        else:
            short_alert = (
                f"Nightly run complete. No anomalies detected in "
                f"{total_packets} packets."
            )
        speak(short_alert)

        speak("Here is the mission briefing.")
        speak(briefing)

    # Persist last scheduled run for UI review
    LAST_SCHEDULED_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(LAST_SCHEDULED_FILE, "w", encoding="utf-8") as f:
        json.dump({
        "timestamp": run_summary["timestamp_readable"],
        "total_packets": run_summary["total_packets"],
        "anomaly_count": run_summary["anomaly_count"],
        "csv_file": run_summary["csv_file"],
        "bin_file": run_summary["bin_file"],
        "report_pdf": run_summary["report_pdf"]
        }, f, indent=2)

    return run_summary
