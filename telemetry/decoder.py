# telemetry/decoder.py
from __future__ import annotations

from pathlib import Path
from typing import Tuple

import pandas as pd

from .telemetry_schema import bytes_to_packet, PACKET_STRUCT, FIELD_NAMES
from .config import DEFAULT_BIN_FILE, DEFAULT_CSV_FILE


def decode_bin_to_df(
    bin_path: Path | None = None,
    save_csv: bool = True,
    csv_path: Path | None = None,
) -> Tuple[pd.DataFrame, Path | None]:
    """
    Decode a .bin file of packets into a pandas DataFrame.
    Optionally save as CSV.
    """
    if bin_path is None:
        bin_path = DEFAULT_BIN_FILE
    if csv_path is None:
        csv_path = DEFAULT_CSV_FILE

    records = []
    size = PACKET_STRUCT.size

    with open(bin_path, "rb") as f:
        while True:
            chunk = f.read(size)
            if not chunk or len(chunk) < size:
                break
            pkt = bytes_to_packet(chunk)
            records.append(pkt)

    df = pd.DataFrame.from_records(records, columns=FIELD_NAMES)

    if save_csv:
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)

    return df, (csv_path if save_csv else None)
