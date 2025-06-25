# File: src/utils/reporting.py

from io import BytesIO

import pandas as pd


def create_report_excel(stats: dict, logs: list, web_vitals_data: list) -> bytes:
    """Membuat file laporan Excel dari statistik, log, dan data web vitals."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame([stats]).to_excel(writer, sheet_name="Ringkasan", index=False)
        pd.DataFrame(logs, columns=["Log Aktivitas"]).to_excel(writer, sheet_name="Log Detail", index=False)
        if web_vitals_data:
            pd.DataFrame(web_vitals_data).to_excel(writer, sheet_name="Web Vitals", index=False)
    return output.getvalue()


def create_ga4_compatible_csv(events: list) -> bytes:
    """Mengubah daftar event menjadi CSV yang kompatibel untuk impor GA4."""
    if not events:
        return b""
    flat_data = []
    for event in events:
        row = {"client_id": event["client_id"], "timestamp_micros": event["timestamp_micros"], "event_name": event["event_name"]}
        for param_key, param_value in event.get("params", {}).items():
            row[f"event_params.{param_key}"] = param_value
        flat_data.append(row)
    return pd.DataFrame(flat_data).to_csv(index=False).encode("utf-8")


def parse_keywords_from_string(kw_string: str) -> dict:
    """Mengurai string 'key:value, key2:value2' menjadi dictionary."""
    keywords = {}
    for item in kw_string.split(","):
        if ":" in item:
            try:
                key, val = item.split(":", 1)
                keywords[key.strip()] = int(val.strip())
            except (ValueError, IndexError):
                pass
    return keywords