"""
Data storage utilities for persisting scan results to CSV and JSON files.
"""

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
CSV_FILE = DATA_DIR / "scans.csv"
JSON_FILE = DATA_DIR / "scans.json"

# Columns in the current CSV format
CSV_COLUMNS = ["ID", "Date", "Company Name", "CNPJ", "Amount Paid", "Payment Method", "Access Key"]

# Columns used by older headerless CSV rows (no ID, no Access Key)
_LEGACY_COLUMNS = ["Date", "Company Name", "CNPJ", "Amount Paid", "Payment Method"]


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _next_id(raw_rows: List[List[str]], has_header: bool, is_new_format: bool) -> int:
    """Return the next sequential integer ID."""
    data_rows = raw_rows[1:] if has_header else raw_rows
    if not data_rows:
        return 1
    if is_new_format:
        # ID is the first column; ID column could be empty for legacy rows kept without header
        try:
            return max(int(row[0]) for row in data_rows if row[0].strip().isdigit()) + 1
        except ValueError:
            pass
    return len(data_rows) + 1


def _read_csv_rows() -> List[Dict[str, str]]:
    """Read CSV rows, supporting both headerless legacy files and the current format with headers."""
    if not CSV_FILE.exists():
        return []

    with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        raw_rows = [row for row in reader if row]

    if not raw_rows:
        return []

    first_row = [cell.strip() for cell in raw_rows[0]]
    has_header = first_row == CSV_COLUMNS or first_row == _LEGACY_COLUMNS
    is_new_format = first_row == CSV_COLUMNS

    # Choose the column names that match the file
    col_names = CSV_COLUMNS if is_new_format else _LEGACY_COLUMNS
    data_rows = raw_rows[1:] if has_header else raw_rows

    rows: List[Dict[str, str]] = []
    for i, row in enumerate(data_rows, start=1):
        normalized = row[: len(col_names)] + [""] * max(0, len(col_names) - len(row))
        record = dict(zip(col_names, normalized))
        # Back-fill missing columns so every dict has all CSV_COLUMNS keys
        if "ID" not in record:
            record["ID"] = str(i)
        if "Access Key" not in record:
            record["Access Key"] = ""
        rows.append(record)
    return rows


def save_scan_to_csv(
    scan_id: int,
    emission_date: str,
    company_name: str,
    cnpj: str,
    amount_paid: float,
    payment_method: str,
    access_key: str,
) -> None:
    """Append a scan summary row to the CSV file."""
    _ensure_data_dir()
    write_header = not CSV_FILE.exists() or CSV_FILE.stat().st_size == 0
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        if write_header:
            writer.writeheader()
        writer.writerow(
            {
                "ID": scan_id,
                "Date": emission_date,
                "Company Name": company_name,
                "CNPJ": cnpj,
                "Amount Paid": amount_paid,
                "Payment Method": payment_method,
                "Access Key": access_key,
            }
        )


def save_scan_to_json(scan_data: Dict[str, Any]) -> None:
    """Append a full scan record to the JSON file."""
    _ensure_data_dir()
    records: List[Dict[str, Any]] = []
    if JSON_FILE.exists():
        try:
            with open(JSON_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        except (json.JSONDecodeError, ValueError):
            records = []
    records.append(scan_data)
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)


def next_scan_id() -> int:
    """Return the next unique sequential scan ID."""
    if not CSV_FILE.exists() or CSV_FILE.stat().st_size == 0:
        return 1
    with open(CSV_FILE, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        raw_rows = [row for row in reader if row]
    if not raw_rows:
        return 1
    first_row = [cell.strip() for cell in raw_rows[0]]
    has_header = first_row == CSV_COLUMNS or first_row == _LEGACY_COLUMNS
    is_new_format = first_row == CSV_COLUMNS
    return _next_id(raw_rows, has_header, is_new_format)


def get_last_scan_from_csv() -> Optional[Dict[str, str]]:
    """Return the last row of the CSV file as a dict, or None if empty."""
    rows = _read_csv_rows()
    return rows[-1] if rows else None


def get_all_scans_from_csv() -> List[Dict[str, str]]:
    """Return all rows from the CSV file as a list of dicts."""
    return _read_csv_rows()


def get_scan_detail_from_json(scan_id: int) -> Optional[Dict[str, Any]]:
    """Return a full scan record from the JSON file by its ID, or None if not found."""
    if not JSON_FILE.exists():
        return None
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            records: List[Dict[str, Any]] = json.load(f)
    except (json.JSONDecodeError, ValueError):
        return None
    for record in records:
        if record.get("id") == scan_id:
            return record
    return None
