# main.py
"""
Simple CLI entry point to test the Hex20 telemetry backend.

Usage:

    python main.py generate
    python main.py decode
    python main.py train
    python main.py detect
    python main.py nightly
    python main.py explain
    python main.py charts
    python main.py ask "your question here"
    python main.py schedule
"""
from __future__ import annotations

import sys
from pprint import pprint

from telemetry.generator import generate_packets
from telemetry.decoder import decode_bin_to_df
from telemetry.anomaly import train_anomaly_model, run_detection, compute_summary_stats
from telemetry.nightly_job import run_nightly_job
from telemetry.scheduler import start_scheduler
from telemetry.inspection import explain_top_anomaly
from telemetry.visual_data import get_timeseries_for_ui, summarize_for_ui
from telemetry.query import ask_telemetry


def cmd_generate():
    path = generate_packets()
    print(f"Generated packets to: {path}")


def cmd_decode():
    df, csv_path = decode_bin_to_df()
    print(f"Decoded {len(df)} packets.")
    print(f"Saved CSV to: {csv_path}")
    print(df.head())


def cmd_train():
    df, _ = decode_bin_to_df()
    model_path = train_anomaly_model(df)
    print(f"Trained Isolation Forest model saved to: {model_path}")


def cmd_detect():
    df, _ = decode_bin_to_df()
    df_detected = run_detection(df)
    stats = compute_summary_stats(df_detected)
    print("Detection complete. Summary:")
    pprint(stats)
    print("\nSample rows:")
    print(df_detected.head())


def cmd_nightly():
    summary = run_nightly_job()
    print("Nightly job completed. Summary:")
    pprint(summary)


def cmd_explain():
    result = explain_top_anomaly()
    print("Top anomaly explanation:\n")

    if "message" in result:
        print(result["message"])
        return

    print(f"Packet index: {result['packet_index']}")
    print(f"Anomaly score: {result['anomaly_score']:.3f}\n")

    print("Packet fields (features):")
    for k, v in result["packet"].items():
        print(f"  {k}: {v}")

    print("\nAI explanation:")
    print(result["explanation"])


def cmd_charts():
    df = get_timeseries_for_ui()
    summary = summarize_for_ui(df)

    print("Time-series data ready for UI:")
    print("Summary:")
    pprint(summary)

    print("\nSample rows:")
    print(df.head())


def cmd_ask(question: str | None):
    if not question:
        
        question = input("Enter your telemetry question: ").strip()

    result = ask_telemetry(question)

    print("Telemetry Q&A\n")
    print(f"Question: {result['question']}\n")
    print("Answer:")
    print(result["answer"])
    print("\n(Internal context preview used for reasoning, not shown to end-user UI)")


def cmd_schedule():
    start_scheduler(hour=2, minute=0)
    print("Scheduler is running in the background. Press Ctrl+C to stop.")
    try:
        import time

        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("Exiting.")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd == "generate":
        cmd_generate()
    elif cmd == "decode":
        cmd_decode()
    elif cmd == "train":
        cmd_train()
    elif cmd == "detect":
        cmd_detect()
    elif cmd == "nightly":
        cmd_nightly()
    elif cmd == "explain":
        cmd_explain()
    elif cmd == "charts":
        cmd_charts()
    elif cmd == "ask":
        
        question = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else None
        cmd_ask(question)
    elif cmd == "schedule":
        cmd_schedule()
    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
