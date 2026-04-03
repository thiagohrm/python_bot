#!/usr/bin/env python3
"""
Example usage of the data_extraction and data_processing modules for extracting table data and creating DataFrames.
"""

from data_extraction import extract_table_data
from data_processing import create_products_dataframe, format_dataframe_for_display


def main():
    """Demonstrate table data extraction and DataFrame creation functionality."""

    # Example HTML content with product table
    html_content = """
    <table id="tabResult">
      <tr>
        <td>
          <span class="txtTit">CREME LEITE NESTLE TP 200G</span>
          <span class="RCod">(Código: 12332)</span>
          <span class="Rqtd"><strong>Qtde.:</strong>1</span>
          <span class="RUN"><strong>UN: </strong>UN0001</span>
          <span class="RvlUnit"><strong>Vl. Unit.:</strong>5,79</span>
        </td>
        <td><span class="valor">5,79</span></td>
      </tr>
      <tr>
        <td>
          <span class="txtTit">ARROZ TIO JOÃO 5KG</span>
          <span class="RCod">(Código: 45678)</span>
          <span class="Rqtd"><strong>Qtde.:</strong>2</span>
          <span class="RUN"><strong>UN: </strong>UN0002</span>
          <span class="RvlUnit"><strong>Vl. Unit.:</strong>12,50</span>
        </td>
        <td><span class="valor">25,00</span></td>
      </tr>
    </table>
    """

    print("🔍 Extracting data from HTML table...")
    print("=" * 60)

    # Extract table data
    table_data = extract_table_data(html_content)
    print(f"📊 Found {len(table_data)} products:")
    print()

    for i, product in enumerate(table_data, 1):
        print(f"{i}. {product['Produto']}")
        print(f"   📋 Code: {product['Código']}")
        print(f"   🔢 Qty: {product['Qtde']}")
        print(f"   📦 Unit: {product['UN']}")
        print(f"   💰 Unit Price: R$ {product['Vl_Unit']:.2f}")
        print(f"   💵 Total: R$ {product['Vl_Total']:.2f}")
        print()

    print("=" * 60)

    # Create DataFrame from extracted data
    print("📈 Creating pandas DataFrame...")
    df = create_products_dataframe(table_data)

    print("📋 DataFrame Info:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print()

    print("📊 DataFrame Content:")
    print(df.to_string(index=False))
    print()

    print("=" * 60)

    # Format DataFrame for display (like in Telegram bot)
    print("💬 Formatted for Telegram display:")
    formatted = format_dataframe_for_display(df)
    print(formatted)

    print("\n" + "=" * 60)

    # Test with empty data
    print("🔍 Testing with empty table data...")
    empty_df = create_products_dataframe([])
    print(f"Empty DataFrame shape: {empty_df.shape}")
    print(f"Is empty: {empty_df.empty}")


if __name__ == "__main__":
    main()