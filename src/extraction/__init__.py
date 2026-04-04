"""
Data extraction and processing module
"""

from src.extraction.data_extraction import (
    extract_div_data,
    extract_company_info,
    extract_table_data,
    extract_total_data,
    extract_emission_info
)
from src.extraction.data_processing import (
    create_products_dataframe,
    format_dataframe_for_display
)

__all__ = [
    'extract_div_data',
    'extract_company_info',
    'extract_table_data',
    'extract_total_data',
    'extract_emission_info',
    'create_products_dataframe',
    'format_dataframe_for_display'
]
