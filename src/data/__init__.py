"""
Data storage module
"""

from src.data.store import (
    save_scan_to_csv,
    save_scan_to_json,
    get_last_scan_from_csv,
    get_all_scans_from_csv,
    get_scan_detail_from_json,
    next_scan_id,
)

__all__ = [
    "save_scan_to_csv",
    "save_scan_to_json",
    "get_last_scan_from_csv",
    "get_all_scans_from_csv",
    "get_scan_detail_from_json",
    "next_scan_id",
]
