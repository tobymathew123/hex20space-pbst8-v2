# telemetry/config.py
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables 
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

for d in (DATA_DIR, MODELS_DIR, REPORTS_DIR, LOGS_DIR):
    d.mkdir(parents=True, exist_ok=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# Paths
DEFAULT_BIN_FILE = DATA_DIR / "telemetry_packets.bin"
DEFAULT_CSV_FILE = DATA_DIR / "telemetry_packets.csv"
MODEL_PATH = MODELS_DIR / "isolation_forest.joblib"
NIGHTLY_LOG = LOGS_DIR / "nightly_runs.log"
