# 🚀 AI-Enabled CubeSat Telemetry Nightly Test Tool  
### (Hex20 Space Internship Assignment)

An **end-to-end AI-powered telemetry simulation and anomaly detection system** designed to replicate how real satellite operations teams perform **nightly health monitoring, anomaly detection, automated analysis, and reporting**.

This system simulates **raw CubeSat telemetry**, stores it in **binary format**, processes it through a **scheduled nightly AI pipeline**, detects anomalies using **machine learning**, generates **AI mission briefings and fix recommendations**, and visualizes everything in a **professional interactive dashboard**.

---

# ✅ REQUIREMENT COMPLETION CHECKLIST

| Requirement | Status |
|------------|--------|
| Define sample CubeSat telemetry packet | ✅ Completed |
| Save raw telemetry packets to `.bin` | ✅ Completed |
| Perform data processing on scheduled time | ✅ Completed |
| Use AI for data processing | ✅ Completed |
| Use AI for human interaction | ✅ Completed |
| Time scheduling must be present | ✅ Minute-level scheduling implemented |
| Interactive GUI must be present | ✅ Streamlit Dashboard |
| AI Feature must be present | ✅ Multiple AI Systems |
| Nightly regression / validation | ✅ Implemented |
| PDF mission reporting | ✅ Implemented |

✅ **ALL MANDATORY & ACCEPTANCE CRITERIA ARE FULLY SATISFIED**

---

# 🧠 CORE SYSTEM CAPABILITIES

✅ Raw Binary Telemetry Simulation  
✅ Automated Nightly AI Processing  
✅ Machine Learning Anomaly Detection (Isolation Forest)  
✅ AI Mission Briefings  
✅ AI Root Cause Analysis  
✅ AI Telemetry Q&A  
✅ Professional PDF Reports  
✅ Fully Interactive Web Dashboard  
✅ User-Configurable Time Scheduling  
✅ Manual Debug Pipeline Controls  

---

# 🎯 PROJECT OBJECTIVE

The goal of this project is to **simulate how real satellite telemetry pipelines operate in the aerospace industry**, including:

- Continuous telemetry monitoring
- Automated nightly health checks
- AI-assisted diagnostic reasoning
- Human-friendly anomaly explanations
- Structured reporting for mission engineers

This project is built **as if it were for a real ground control system**, not just as a demo.

---

# 🛰️ TELEMETRY PACKET DESIGN

Each telemetry packet represents a single CubeSat state snapshot.

| Field | Units | Description |
|-------|--------|-------------|
| `timestamp` | seconds | Epoch time |
| `battery_v` | Volts | Battery voltage |
| `panel_i` | Amps | Solar panel current |
| `temp_c` | °C | Internal spacecraft temperature |
| `gyro_x` | rad/s | Angular velocity (X) |
| `gyro_y` | rad/s | Angular velocity (Y) |
| `gyro_z` | rad/s | Angular velocity (Z) |
| `mode` | int | Operational mode |

These packets are **not stored as text** — they are written as **real binary structs**, exactly how embedded flight systems record telemetry.

---

# 📂 RAW BINARY TELEMETRY STORAGE

All telemetry packets are stored as:


✅ This file contains **true raw binary data**  
✅ It is regenerated every run  
✅ It is decoded only for processing  
✅ It is excluded from GitHub using `.gitignore`

---

# 🧪 MACHINE LEARNING – ANOMALY DETECTION

### Model Used:
**Isolation Forest**

### Why Isolation Forest?
- No labeled anomaly dataset required
- Designed for outlier detection
- Performs well on high-dimensional telemetry
- Industry-accepted for log & telemetry anomaly detection

### Pipeline:
1. Normal data is sampled
2. Model is trained
3. All packets are scored
4. High anomaly scores are flagged
5. Results sent to AI reasoning system

---

# 🧠 AI SYSTEMS IMPLEMENTED

| AI System | Purpose |
|-----------|---------|
| AI Mission Briefing | Converts raw stats into engineering summary |
| AI Anomaly Explanation | Explains why a specific packet is anomalous |
| AI Telemetry Q&A | Allows natural language queries |
| AI Engineering Fixes | Suggests checks & corrective actions |

All AI interactions are performed using **OpenAI APIs**.

---

# 📄 AUTOMATED PDF REPORT SYSTEM

Each nightly run automatically generates a **professional PDF report** containing:

✅ Timestamp in IST  
✅ Packet count  
✅ Anomaly count  
✅ Anomaly rate (%)  
✅ Key telemetry statistics  
✅ AI-generated mission briefing  
✅ AI-generated key findings  
✅ AI-generated engineering recommendations  

Reports are stored at:


These reports are suitable for:
- Operations review  
- Engineering diagnostics  
- Management reporting  

---

# 🗓️ NIGHTLY SCHEDULING SYSTEM

✅ Minute-level configurable scheduling  
✅ User selects exact **HH:MM IST**
✅ Background scheduler executes entire AI pipeline automatically
✅ Includes:
- Packet generation
- Binary decoding
- Model training
- Anomaly detection
- AI mission briefing
- PDF creation

This implements **true unattended nightly processing**.

---

# 🖥️ INTERACTIVE GUI DASHBOARD

Built using **Streamlit**, the GUI provides:

✅ Mission Summary Cards  
✅ AI Nightly Briefings  
✅ AI Anomaly Analysis  
✅ Telemetry Q&A Interface  
✅ Manual Pipeline Execution  
✅ Time Scheduling Controls  
✅ Anomaly Highlighted Graphs  
✅ Live Anomaly Table  
✅ PDF Report Access  

---

# ⚙️ FULL SYSTEM ARCHITECTURE

```text
Telemetry Generator (.bin)
        ↓
Binary Decoder → CSV
        ↓
Isolation Forest ML Model
        ↓
Anomaly Detection
        ↓
AI Mission Briefing + AI Diagnostics + AI Recommendations
        ↓
Scheduled PDF Report Generator
        ↓
Streamlit Interactive GUI
```
## 🛠️ Installation Guide (Complete Setup)

### ✅ Step 1 — Clone the Repository
```bash
git clone https://github.com/tobymathew123/hex20space-pbst8-v2.git
cd hex20space-pbst8-v2
```

---

### ✅ Step 2 — Create a Virtual Environment
```bash
python -m venv .venv
```

---

### ✅ Step 3 — Activate the Virtual Environment

**Windows (PowerShell / CMD):**
```bash
.venv\Scripts\activate
```

**Mac / Linux:**
```bash
source .venv/bin/activate
```

---

### ✅ Step 4 — Upgrade pip (Recommended)
```bash
python -m pip install --upgrade pip
```

---

### ✅ Step 5 — Install All Required Dependencies

**If `requirements.txt` exists:**
```bash
pip install -r requirements.txt
```

**If not:**
```bash
pip install streamlit scikit-learn pandas numpy plotly reportlab apscheduler openai python-dotenv
```

---

### ✅ Step 6 — Set Your OpenAI API Key

#### Method 1: Using `.env` File (Recommended)

Create a file named `.env` in the project root and add:

```env
OPENAI_API_KEY=your_api_key_here
```

---

#### Method 2: Set Directly in Terminal

**Windows PowerShell:**
```bash
setx OPENAI_API_KEY "your_api_key_here"
```

**Mac / Linux:**
```bash
export OPENAI_API_KEY="your_api_key_here"
```

✅ Restart your terminal after setting the key.

---

### ✅ Step 7 — Run the Application
```bash
streamlit run app.py
```

---

### ✅ After Successful Launch, You Should See:

- ✅ The interactive Streamlit dashboard
- ✅ Manual pipeline controls
- ✅ Nightly scheduling controls
- ✅ AI Mission Briefing section
- ✅ AI Anomaly Analysis
- ✅ Interactive graphs & anomaly tables
- ✅ Auto-generated PDF reports inside the `reports/` folder
- ✅ .bin files are inside the `data/` folder to view the raw data
