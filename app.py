import streamlit as st
import plotly.express as px
from datetime import datetime, time as dt_time, timedelta, timezone
import json
from pathlib import Path

from telemetry.nightly_job import run_nightly_job
from telemetry.visual_data import get_timeseries_for_ui, summarize_for_ui
from telemetry.inspection import explain_top_anomaly
from telemetry.query import ask_telemetry
from telemetry.scheduler import start_scheduler
from telemetry.generator import generate_packets
from telemetry.decoder import decode_bin_to_df
from telemetry.anomaly import train_anomaly_model, run_detection, compute_summary_stats

IST = timezone(timedelta(hours=5, minutes=30))
LAST_SCHEDULED_FILE = Path("data/last_scheduled_run.json")

def load_last_scheduled_run():
    if not LAST_SCHEDULED_FILE.exists():
        return None
    try:
        with open(LAST_SCHEDULED_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


st.set_page_config(
    page_title="AI Telemetry Nightly Test Tool",
    layout="wide",
)

st.title("🚀 AI-Enabled Telemetry Nightly Test Tool")
st.markdown("**CubeSat Health Monitoring • Anomaly Detection • AI Mission Briefing**")

if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = False

if "active_run_source" not in st.session_state:
    st.session_state["active_run_source"] = None


# ===================== SIDEBAR =====================

st.sidebar.header("Controls")

st.sidebar.subheader("Manual Pipeline Steps")

manual_step = st.sidebar.selectbox(
    "Select step to run:",
    [
        "None",
        "Generate packets (.bin)",
        "Decode .bin → CSV",
        "Train anomaly model",
        "Run detection",
    ],
)

if st.sidebar.button("Run Selected Step"):
    if manual_step == "Generate packets (.bin)":
        path = generate_packets()
        st.sidebar.success(f"Generated sample packets to: {path}")
    elif manual_step == "Decode .bin → CSV":
        df_dec, csv_path = decode_bin_to_df()
        st.sidebar.success(f"Decoded {len(df_dec)} packets to CSV: {csv_path}")
    elif manual_step == "Train anomaly model":
        df_dec, _ = decode_bin_to_df()
        model_path = train_anomaly_model(df_dec)
        st.sidebar.success(f"Trained model saved to: {model_path}")
    elif manual_step == "Run detection":
        df_dec, _ = decode_bin_to_df()
        df_det = run_detection(df_dec)
        stats = compute_summary_stats(df_det)
        st.sidebar.success(
            f"Detection done. Anomalies: {stats.get('anomaly_count', 0)} "
            f"/ {stats.get('total_packets', len(df_det))}"
        )
        st.session_state["data_loaded"] = True


st.sidebar.markdown("---")

if st.sidebar.button("▶ Run Nightly Test"):
    with st.spinner("Running full nightly pipeline (Generate → Detect → AI Briefing)..."):
        summary = run_nightly_job()
    st.session_state["last_nightly_summary"] = summary
    st.session_state["data_loaded"] = True
    st.session_state["active_run_source"] = "manual"
    st.sidebar.success("Nightly job completed!")


st.sidebar.markdown("---")

st.sidebar.subheader("Time Scheduling (IST)")

schedule_time = st.sidebar.time_input(
    "Daily run time (HH:MM, IST)",
    value=dt_time(hour=2, minute=0),
)

if st.sidebar.button("Start Daily Scheduler"):
    start_scheduler(hour=schedule_time.hour, minute=schedule_time.minute)
    st.sidebar.success(
        f"Nightly job scheduled at {schedule_time.hour:02d}:{schedule_time.minute:02d} IST."
    )


# ===================== RUN SELECTION =====================

st.markdown("---")
st.subheader("📂 Select Telemetry Run to Review")

run_option = st.radio(
    "Choose which telemetry run to inspect:",
    [ "Latest Manual Run", "Last Scheduled Nightly Run"],
    horizontal=True,
)

if run_option == "Latest Manual Run":
    if "last_nightly_summary" in st.session_state:
        st.session_state["data_loaded"] = True
        st.session_state["active_run_source"] = "manual"
    else:
        st.warning("No manual nightly run available yet.")

elif run_option == "Last Scheduled Nightly Run":
    scheduled = load_last_scheduled_run()
    if scheduled is None:
        st.warning("No scheduled nightly run available yet.")
    else:
        st.session_state["data_loaded"] = True
        st.session_state["active_run_source"] = "scheduled"


# ===================== LOAD DATA =====================

df = None
summary = None

if st.session_state["data_loaded"]:
    df = get_timeseries_for_ui()
    summary = summarize_for_ui(df)


# ===================== MISSION SUMMARY =====================

st.markdown("---")
st.subheader("📊 Mission Summary")

if summary is None:
    st.info("No telemetry run loaded yet.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Packets", summary["total_packets"])
    col2.metric("Anomalies Detected", summary["anomaly_count"])
    col3.metric("Time Span (IST)",
        f"{datetime.fromtimestamp(summary['first_timestamp'], IST).strftime('%H:%M:%S')} → "
        f"{datetime.fromtimestamp(summary['last_timestamp'], IST).strftime('%H:%M:%S')}"
    )


# ===================== AI BRIEFING =====================

st.markdown("---")
st.subheader("🛰️ AI Nightly Mission Briefing")

if st.session_state["active_run_source"] == "manual":
    st.write(st.session_state["last_nightly_summary"]["briefing"])
elif st.session_state["active_run_source"] == "scheduled":
    scheduled = load_last_scheduled_run()
    st.info(
        "This briefing corresponds to the last scheduled nightly run. "
        "Detailed insights are available in the generated report."
    )
else:
    st.info("Select a telemetry run to view the mission briefing.")


# ===================== AI Q&A + ANALYSIS =====================

if df is not None:
    st.markdown("---")
    st.subheader("💬 Ask Your Telemetry (AI Q&A)")

    user_question = st.text_input("Ask anything about the telemetry data:")

    if st.button("Ask AI"):
        if user_question.strip():
            result = ask_telemetry(user_question)
            st.success(result["answer"])

    st.markdown("---")
    st.subheader("🧠 AI Anomaly Analysis")

    if st.button("Analyze Most Severe Anomaly"):
        result = explain_top_anomaly()
        if "message" in result:
            st.warning(result["message"])
        else:
            st.success(result["explanation"])


# ===================== GRAPHS =====================

if df is not None:
    st.markdown("---")
    with st.expander("📈 Telemetry Time-Series with Anomalies", expanded=False):
        for feature, label in [
            ("battery_v", "Battery Voltage (V)"),
            ("temp_c", "Temperature (°C)"),
            ("panel_i", "Panel Current (A)"),
        ]:
            fig = px.scatter(
                df,
                x="timestamp",
                y=feature,
                color="is_anomaly",
                title=f"{label} vs Time",
            )
            st.plotly_chart(fig, use_container_width=True)


st.markdown("---")
st.caption("AI Nightly Test Tool •")
