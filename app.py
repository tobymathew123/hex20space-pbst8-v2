import streamlit as st
import plotly.express as px
from datetime import datetime, time as dt_time, timedelta, timezone

from telemetry.nightly_job import run_nightly_job
from telemetry.visual_data import get_timeseries_for_ui, summarize_for_ui
from telemetry.inspection import explain_top_anomaly
from telemetry.query import ask_telemetry
from telemetry.scheduler import start_scheduler
from telemetry.generator import generate_packets
from telemetry.decoder import decode_bin_to_df
from telemetry.anomaly import train_anomaly_model, run_detection, compute_summary_stats

IST = timezone(timedelta(hours=5, minutes=30))

st.set_page_config(
    page_title="AI Telemetry Nightly Test Tool",
    layout="wide",
)

st.title("🚀 AI-Enabled Telemetry Nightly Test Tool")
st.markdown("**CubeSat Health Monitoring • Anomaly Detection • AI Mission Briefing**")

if "data_loaded" not in st.session_state:
    st.session_state["data_loaded"] = False


# SIDEBAR CONTROLS

st.sidebar.header("Controls")

# Manual pipeline steps
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
    else:
        st.sidebar.info("Select a step to run.")

st.sidebar.markdown("---")

# One-click nightly demo
if st.sidebar.button("▶ Run Nightly Test (Demo)"):
    with st.spinner("Running full nightly pipeline (Generate → Detect → AI Briefing)..."):
        summary = run_nightly_job()
    st.session_state["last_nightly_summary"] = summary
    st.session_state["data_loaded"] = True
    st.sidebar.success("Nightly job completed!")
    st.sidebar.write(f"Anomalies: {summary['anomaly_count']}")
    st.sidebar.write(f"PDF report: {summary['report_pdf']}")

st.sidebar.markdown("---")


st.sidebar.subheader("Time Scheduling (IST)")

default_time = dt_time(hour=2, minute=0)
schedule_time = st.sidebar.time_input(
    "Daily run time (HH:MM, IST)",
    value=default_time,
    help="Nightly job will run automatically at this local time every day.",
)

if st.sidebar.button("Start Daily Scheduler"):
    start_scheduler(hour=schedule_time.hour, minute=schedule_time.minute)
    st.sidebar.success(
        f"Scheduler started. Nightly job will run automatically at "
        f"{schedule_time.hour:02d}:{schedule_time.minute:02d} IST each day."
    )

st.sidebar.markdown("---")
st.sidebar.caption(
    "Manual steps + automatic scheduler together show the full nightly test workflow."
)


# LOAD DATA
df = None
summary = None

if st.session_state["data_loaded"]:
    df = get_timeseries_for_ui()
    summary = summarize_for_ui(df)


# MISSION SUMMARY

st.subheader("📊 Mission Summary")


def to_ist_time(ts_int: int) -> str:
    try:
        dt = datetime.fromtimestamp(ts_int, tz=IST)
        return dt.strftime("%H:%M:%S")
    except Exception:
        return "-"


def to_ist_date(ts_int: int) -> str:
    try:
        dt = datetime.fromtimestamp(ts_int, tz=IST)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return "-"


if summary is None:
    st.info("No telemetry run loaded yet. Run the nightly test demo or detection from the sidebar.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Packets", summary["total_packets"])
    col2.metric("Anomalies Detected", summary["anomaly_count"])
    span_val = f"{to_ist_time(summary['first_timestamp'])} → {to_ist_time(summary['last_timestamp'])}"
    col3.metric("Time Span (IST)", span_val)
    date_span = f"{to_ist_date(summary['first_timestamp'])} → {to_ist_date(summary['last_timestamp'])}"
    st.caption(f"Date span (IST): {date_span}")


# AI NIGHTLY MISSION BRIEFING

st.markdown("---")
st.subheader("🛰️ AI Nightly Mission Briefing")

if "last_nightly_summary" in st.session_state:
    st.write(st.session_state["last_nightly_summary"]["briefing"])
else:
    st.info("Run the nightly test demo from the sidebar to generate an AI mission briefing.")


# AI Q&A + ANOMALY ANALYSIS 

if df is not None:
    st.markdown("---")
    st.subheader("💬 Ask Your Telemetry (AI Q&A)")

    user_question = st.text_input("Ask anything about the telemetry data:")

    if st.button("Ask AI"):
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            with st.spinner("AI is analyzing your question..."):
                result = ask_telemetry(user_question)

            st.write("**Question:**")
            st.info(result["question"])

            st.write("**AI Answer:**")
            st.success(result["answer"])

    # --- AI anomaly analysis section ---
    st.markdown("---")
    st.subheader("🧠 AI Anomaly Analysis")

    if summary is not None:
        total = summary["total_packets"]
        acount = summary["anomaly_count"]
        rate = (acount / total * 100.0) if total > 0 else 0.0
        st.caption(f"Current run: {acount} anomalies out of {total} packets ({rate:.1f}% anomaly rate).")

    st.write(
        "This tool inspects the **most anomalous packet** from the latest run and "
        "explains which subsystem might be affected and why the model flagged it."
    )

    if st.button("Analyze Most Severe Anomaly"):
        with st.spinner("AI is analyzing the most anomalous packet..."):
            result = explain_top_anomaly()

        if "message" in result:
            st.warning(result["message"])
        else:
            st.write("**Packet Index (in current run):**", result["packet_index"])
            st.write("**Anomaly Score:**", f"{result['anomaly_score']:.3f}")
            st.write("**Packet Values:**")
            st.json(result["packet"])
            st.write("**AI Interpretation:**")
            st.success(result["explanation"])

   
    # GRAPHS + TABLE
 
    st.markdown("---")
    with st.expander("📈 Telemetry Time-Series with Anomalies (click to expand)", expanded=False):
        st.subheader("Telemetry Time-Series")

        def plot_feature(feature_name, y_label):
            fig = px.scatter(
                df,
                x="timestamp",
                y=feature_name,
                color="is_anomaly",
                title=f"{feature_name} vs Time (Anomalies Highlighted)",
                labels={
                    "timestamp": "Time (epoch seconds)",
                    feature_name: y_label,
                    "is_anomaly": "Is Anomaly",
                },
            )
            st.plotly_chart(fig, use_container_width=True)

        tab1, tab2, tab3 = st.tabs(["Battery Voltage", "Temperature", "Panel Current"])

        with tab1:
            plot_feature("battery_v", "Battery Voltage (V)")
        with tab2:
            plot_feature("temp_c", "Temperature (°C)")
        with tab3:
            plot_feature("panel_i", "Panel Current (A)")

        st.markdown("---")
        st.subheader("🚨 Detected Anomalies (Table)")
        anom_df = df[df["is_anomaly"] == True].copy()
        st.dataframe(
            anom_df[[
                "timestamp",
                "battery_v",
                "panel_i",
                "temp_c",
                "gyro_x",
                "gyro_y",
                "gyro_z",
                "mode",
                "anomaly_score",
            ]].sort_values("anomaly_score", ascending=False),
            use_container_width=True,
        )

# FOOTER
st.markdown("---")
st.caption(
    "AI Telemetry Tool • Isolation Forest + OpenAI • Manual pipeline + scheduled nightly automation (IST)"
)
