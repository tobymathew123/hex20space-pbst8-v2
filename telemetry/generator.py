# telemetry/generator.py
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import random

from .telemetry_schema import (
    generate_normal_packet,
    inject_fault,
    packet_to_bytes,
    PACKET_STRUCT,
)
from .config import DEFAULT_BIN_FILE


def generate_packets(
    n_packets: int = 500,
    out_path: Path | None = None,
    fault_rate: float = 0.02,  
    fault_scenarios: Optional[List[str]] = None,
) -> Path:
    """
    Generate a number of telemetry packets and save them as a .bin file.

    :param n_packets: how many packets to generate
    :param out_path: where to save; default DEFAULT_BIN_FILE
    :param fault_rate: probability that a packet becomes anomalous
    :param fault_scenarios: list of scenario names to choose from
    :return: path to the created .bin file
    """
    if out_path is None:
        out_path = DEFAULT_BIN_FILE

    if fault_scenarios is None:
        fault_scenarios = ["power_drop", "thermal_spike", "attitude_issue"]

    now = int(time.time())

    with open(out_path, "wb") as f:
        for i in range(n_packets):
            ts = now + i  
            p = generate_normal_packet(ts)

            is_fault = random.random() < fault_rate
            if is_fault:
                scenario = random.choice(fault_scenarios)
                p = inject_fault(p, scenario)

            f.write(packet_to_bytes(p))

    return out_path
