"""
Data processing utilities for creating and manipulating pandas DataFrames.
"""

import pandas as pd
from typing import List, Dict, Any

from config import EXPECTED_COLUMNS


def create_products_dataframe(table_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a pandas DataFrame from extracted table data."""
    if not table_data:
        return pd.DataFrame()

    df = pd.DataFrame(table_data)

    # Ensure all expected columns exist
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Reorder columns
    df = df[EXPECTED_COLUMNS]

    return df


def format_dataframe_for_display(df: pd.DataFrame) -> str:
    """Format a DataFrame for display in Telegram messages."""
    if df.empty:
        return "No data available."

    response = f"📊 Stored Products Data ({len(df)} items):\n\n"

    # Format as a simple table
    for idx, row in df.iterrows():
        response += f"🔹 {row['Produto']}\n"
        response += f"   Code: {row['Código']} | Qty: {row['Qtde']} | Unit: {row['UN']}\n"
        response += f"   Price: R$ {row['Vl_Unit']:.2f} | Total: R$ {row['Vl_Total']:.2f}\n\n"

    # Add summary
    total_value = df['Vl_Total'].sum()
    response += f"💰 Total Value: R$ {total_value:.2f}"

    return response