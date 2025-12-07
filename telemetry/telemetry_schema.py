# telemetry/telemetry_schema.py
import struct
import random
import time
from typing import Dict, Any, List

#health parameters
#   uint32 timestamp
#   float32 battery_v
#   float32 panel_i
#   float32 temp_c
#   float32 gyro_x
#   float32 gyro_y
#   float32 gyro_z
#   uint8  mode
PACKET_STRUCT = struct.Struct(">I f f f f f f B")

FIELD_NAMES: List[str] = [
    "timestamp",
    "battery_v",
    "panel_i",
    "temp_c",
    "gyro_x",
    "gyro_y",
    "gyro_z",
    "mode",
]

MODES = {
    0: "IDLE",
    1: "NOMINAL",
    2: "SAFE",
    3: "MANEUVER",
}


def generate_normal_packet(ts: int | None = None) -> Dict[str, Any]:
    """Generate a single 'normal' CubeSat telemetry packet."""
    if ts is None:
        ts = int(time.time())

    battery_v = random.normalvariate(7.4, 0.2)      # volts
    panel_i = max(0.0, random.normalvariate(1.2, 0.3))  # amps
    temp_c = random.normalvariate(35.0, 5.0)        # degrees C
    gyro_x = random.normalvariate(0.0, 0.02)        # deg/s
    gyro_y = random.normalvariate(0.0, 0.02)
    gyro_z = random.normalvariate(0.0, 0.02)
    mode = random.choices([0, 1, 2, 3], weights=[0.1, 0.7, 0.1, 0.1])[0]

    return {
        "timestamp": ts,
        "battery_v": battery_v,
        "panel_i": panel_i,
        "temp_c": temp_c,
        "gyro_x": gyro_x,
        "gyro_y": gyro_y,
        "gyro_z": gyro_z,
        "mode": mode,
    }


def inject_fault(packet: Dict[str, Any], scenario: str) -> Dict[str, Any]:
    """Introduce an anomaly according to a fault scenario."""
    p = packet.copy()

    if scenario == "power_drop":
        p["battery_v"] -= random.uniform(1.0, 2.5)
        p["panel_i"] += random.uniform(0.5, 1.0)
        p["mode"] = 2  # SAFE
    elif scenario == "thermal_spike":
        p["temp_c"] += random.uniform(15.0, 30.0)
    elif scenario == "attitude_issue":
        p["gyro_x"] += random.uniform(-0.5, 0.5)
        p["gyro_y"] += random.uniform(-0.5, 0.5)
        p["gyro_z"] += random.uniform(-0.5, 0.5)
        p["mode"] = 3  # MANEUVER
    # you can add more scenarios later

    return p


def packet_to_bytes(packet: Dict[str, Any]) -> bytes:
    """Serialize a packet dict into binary according to PACKET_STRUCT."""
    return PACKET_STRUCT.pack(
        int(packet["timestamp"]),
        float(packet["battery_v"]),
        float(packet["panel_i"]),
        float(packet["temp_c"]),
        float(packet["gyro_x"]),
        float(packet["gyro_y"]),
        float(packet["gyro_z"]),
        int(packet["mode"]),
    )


def bytes_to_packet(payload: bytes) -> Dict[str, Any]:
    """Deserialize binary payload into a packet dict."""
    unpacked = PACKET_STRUCT.unpack(payload)
    return dict(zip(FIELD_NAMES, unpacked))
