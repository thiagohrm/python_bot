#!/usr/bin/env python
"""
Example usage of the extract_div_data function.
This demonstrates how to extract structured data from HTML divs.
"""

import os
import sys

# Set dummy token for example
os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_example'

sys.path.insert(0, '.')

from main import extract_div_data

# Example HTML with company information
html_example = '''
<div id="conteudo">
  <div id="avisos">
  </div>
  <div class="txtCenter">
    <div id="u20" class="txtTopo">GERALDO BENEDETE COMPANHIA LTDA</div>
    <div class="text">
      CNPJ:
      45.477.452/0001-05
    </div>
    <div class="text">
      AVENIDA GETULIO VARGAS
      ,
      339
      ,
      
      ,
      BAMBU
      ,
      PORTO FELIZ
      ,
      SP
    </div>
  </div>
</div>
'''

# Extract data from the div
result = extract_div_data(html_example)
print("Extracted Data:")
print("=" * 50)
print(result)
print("=" * 50)

# Example with custom div ID
html_custom = '''
<div id="custom_div">
    <div class="txtTopo">ACME CORPORATION</div>
    <div class="text">CNPJ: 99.999.999/0001-00</div>
    <div class="text">RUA PRINCIPAL, 1000, SAO PAULO, SP</div>
</div>
'''

result2 = extract_div_data(html_custom, div_id='custom_div')
print("\nCustom Div Example:")
print("=" * 50)
print(result2)
print("=" * 50)
