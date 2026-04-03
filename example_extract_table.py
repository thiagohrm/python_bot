#!/usr/bin/env python3
"""
Example script demonstrating table data extraction and DataFrame creation.
"""

import os
os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy'

from main import extract_table_data, create_products_dataframe

# Example HTML table (similar to your provided structure)
html_with_table = '''
<table border="0" align="center" cellpadding="0" cellspacing="0" id="tabResult" data-filter="true">
  <tr id="Item + 1">
    <td valign="top">
      <span class="txtTit">CREME LEITE NESTLE TP 200G</span>
      <span class="RCod">
        (Código:
        12332
        )
      </span>
      <br>
      <span class="Rqtd">
        <strong>Qtde.:</strong>1</span>
      <span class="RUN">
        <strong>UN: </strong>UN0001</span>
      <span class="RvlUnit">
        <strong>Vl. Unit.:</strong>
        5,79</span>
    </td>
    <td align="right" valign="top" class="txtTit noWrap">
      Vl. Total
      <br><span class="valor">5,79</span></td>
  </tr>
  <tr id="Item + 2">
    <td valign="top">
      <span class="txtTit">ARROZ BRANCO 5KG</span>
      <span class="RCod">
        (Código:
        45678
        )
      </span>
      <br>
      <span class="Rqtd">
        <strong>Qtde.:</strong>2</span>
      <span class="RUN">
        <strong>UN: </strong>UN0002</span>
      <span class="RvlUnit">
        <strong>Vl. Unit.:</strong>
        12,50</span>
    </td>
    <td align="right" valign="top" class="txtTit noWrap">
      Vl. Total
      <br><span class="valor">25,00</span></td>
  </tr>
</table>
'''

print("🔍 Extracting table data from HTML...")
table_data = extract_table_data(html_with_table)

print(f"📊 Found {len(table_data)} products:")
for i, product in enumerate(table_data, 1):
    print(f"\n{i}. {product['Produto']}")
    print(f"   Code: {product['Código']}")
    print(f"   Qty: {product['Qtde']}")
    print(f"   Unit: {product['UN']}")
    print(f"   Unit Price: R$ {product['Vl_Unit']:.2f}")
    print(f"   Total: R$ {product['Vl_Total']:.2f}")

print("\n📋 Creating pandas DataFrame...")
df = create_products_dataframe(table_data)

print("\nDataFrame Info:")
print(df)
print(f"\nTotal Products: {len(df)}")
print(f"Total Value: R$ {df['Vl_Total'].sum():.2f}")

print("\n✅ Table extraction and DataFrame creation successful!")
print("The bot will automatically extract this data when it finds tables in QR code URLs.")