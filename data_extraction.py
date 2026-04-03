"""
HTML data extraction utilities for parsing structured data from web pages.
"""

import re
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from config import DEFAULT_DIV_ID, DEFAULT_TABLE_ID


def extract_div_data(html_content: str, div_id: str = DEFAULT_DIV_ID) -> str:
    """Extract structured data from specific div elements in HTML."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        target_div = soup.find('div', id=div_id)

        if not target_div:
            return "❌ Error: Target div not found"

        # Extract company name (from txtTopo class)
        company_div = target_div.find('div', class_='txtTopo')
        company_name = company_div.get_text(strip=True) if company_div else 'N/A'

        # Extract all text divs with class 'text'
        text_divs = target_div.find_all('div', class_='text')
        data_lines = []

        for div in text_divs:
            # Clean up text by normalizing whitespace
            text = div.get_text()
            # Replace multiple whitespace characters (including newlines) with single space
            text = re.sub(r'\s+', ' ', text).strip()
            if text:
                data_lines.append(text)

        # Format the result
        result = f"🏢 Company: {company_name}\n\n"
        for i, line in enumerate(data_lines):
            if 'CNPJ' in line:
                result += f"📋 {line}\n"
            elif 'AVENIDA' in line or 'RUA' in line or 'PRACA' in line:
                result += f"📍 {line}\n"
            else:
                result += f"{line}\n"

        return result
    except Exception as e:
        return f"❌ Error extracting div data: {str(e)}"


def extract_table_data(html_content: str, table_id: str = DEFAULT_TABLE_ID) -> List[Dict[str, Any]]:
    """Extract table data and return as list of dictionaries for pandas DataFrame."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        table = soup.find('table', id=table_id)

        if not table:
            return []

        products = []

        # Find all table rows (skip header if exists)
        rows = table.find_all('tr')

        for row in rows:
            # Skip rows that don't contain product data
            if not row.find('span', class_='txtTit'):
                continue

            product_data = {}

            # Extract product name
            name_span = row.find('span', class_='txtTit')
            if name_span:
                product_data['Produto'] = name_span.get_text(strip=True)

            # Extract code
            code_span = row.find('span', class_='RCod')
            if code_span:
                # Extract number from "(Código: 12332 )"
                code_text = code_span.get_text()
                code_match = re.search(r'Código:\s*(\d+)', code_text)
                product_data['Código'] = code_match.group(1) if code_match else ''

            # Extract quantity
            qty_span = row.find('span', class_='Rqtd')
            if qty_span:
                qty_text = qty_span.get_text()
                qty_match = re.search(r'Qtde\.:\s*(\d+)', qty_text)
                product_data['Qtde'] = int(qty_match.group(1)) if qty_match else 0

            # Extract unit
            unit_span = row.find('span', class_='RUN')
            if unit_span:
                unit_text = unit_span.get_text()
                unit_match = re.search(r'UN:\s*([^\s]+)', unit_text)
                product_data['UN'] = unit_match.group(1) if unit_match else ''

            # Extract unit value
            unit_val_span = row.find('span', class_='RvlUnit')
            if unit_val_span:
                val_text = unit_val_span.get_text()
                val_match = re.search(r'Vl\. Unit\.:\s*([^\s]+)', val_text)
                if val_match:
                    # Convert Brazilian format (5,79) to float (5.79)
                    val_str = val_match.group(1).replace(',', '.')
                    try:
                        product_data['Vl_Unit'] = float(val_str)
                    except ValueError:
                        product_data['Vl_Unit'] = 0.0

            # Extract total value
            total_span = row.find('span', class_='valor')
            if total_span:
                total_text = total_span.get_text(strip=True)
                try:
                    # Convert Brazilian format to float
                    product_data['Vl_Total'] = float(total_text.replace(',', '.'))
                except ValueError:
                    product_data['Vl_Total'] = 0.0

            # Only add if we have at least a product name
            if product_data.get('Produto'):
                products.append(product_data)

        return products
    except Exception as e:
        print(f"Error extracting table data: {str(e)}")
        return []


def extract_total_data(html_content: str, div_id: str = "totalNota") -> Dict[str, Any]:
    """Extract total payment data from the totalNota div."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        total_div = soup.find('div', id=div_id)

        if not total_div:
            return {}

        totals = {}

        # Find all divs with id="linhaTotal" and id="linhaForma"
        total_rows = total_div.find_all('div', id=['linhaTotal', 'linhaForma'])

        for row in total_rows:
            label = row.find('label')
            span = row.find('span', class_='totalNumb')

            if label and span:
                label_text = label.get_text(strip=True)
                span_text = span.get_text(strip=True)

                # Map labels to keys
                if 'Qtd. total de itens' in label_text:
                    totals['total_items'] = int(span_text) if span_text.isdigit() else 0
                elif 'Valor a pagar R$' in label_text:
                    # Convert Brazilian format to float
                    totals['amount_to_pay'] = float(span_text.replace(',', '.')) if span_text else 0.0
                elif 'Troco' in label.get_text(strip=True):
                    totals['change'] = float(span_text.replace(',', '.')) if span_text else 0.0

        # Extract payment method and amount paid - they have a different structure
        # Find all spans with class 'totalNumb' that contain amounts
        amount_spans = total_div.find_all('span', class_='totalNumb')
        payment_method_labels = total_div.find_all('label', class_='tx')

        # The payment method is in a label with class 'tx'
        for pm_label in payment_method_labels:
            pm_text = pm_label.get_text(strip=True)
            if 'Cartão' in pm_text or 'Dinheiro' in pm_text or 'PIX' in pm_text:
                totals['payment_method'] = pm_text
                # The next span after this label should be the amount paid
                # Find the parent div and get the next span
                parent_div = pm_label.find_parent('div', id='linhaTotal')
                if parent_div:
                    amount_span = parent_div.find('span', class_='totalNumb')
                    if amount_span and amount_span.get_text(strip=True):
                        amount_text = amount_span.get_text(strip=True)
                        totals['amount_paid'] = float(amount_text.replace(',', '.')) if amount_text else 0.0
                break

        return totals
    except Exception as e:
        print(f"Error extracting total data: {str(e)}")
        return {}


def extract_emission_info(html_content: str, div_id: str = "infos") -> Dict[str, Any]:
    """Extract emission date and other general info from the infos div."""
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        infos_div = soup.find('div', id=div_id)

        if not infos_div:
            return {}

        info = {}

        # Find the li element containing the information
        li_element = infos_div.find('li')
        if li_element:
            text_content = li_element.get_text()

            # Extract emission date using regex - match DD/MM/YYYY HH:MM:SS pattern
            emission_match = re.search(r'Emissão:\s*(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2})', text_content)
            if emission_match:
                info['emission_date'] = emission_match.group(1).strip()
            else:
                # Fallback: try to extract just the date-like pattern after "Emissão:"
                emission_match = re.search(r'Emissão:\s*([^\n\-]+)', text_content)
                if emission_match:
                    info['emission_date'] = emission_match.group(1).strip()

            # Extract protocol - improve regex to capture just the number
            protocol_match = re.search(r'Protocolo de Autorização:\s*(\d+)', text_content)
            if protocol_match:
                info['authorization_protocol'] = protocol_match.group(1).strip()

            # Extract environment
            if 'Ambiente de Produção' in text_content:
                info['environment'] = 'Produção'
            elif 'Ambiente de Homologação' in text_content:
                info['environment'] = 'Homologação'

        return info
    except Exception as e:
        print(f"Error extracting emission info: {str(e)}")
        return {}