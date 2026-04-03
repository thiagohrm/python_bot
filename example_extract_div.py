#!/usr/bin/env python3
"""
Example usage of the data_extraction module for extracting structured data from HTML div elements.
"""

from data_extraction import extract_div_data


def main():
    """Demonstrate div data extraction functionality."""

    # Example HTML content with company information
    html_content = """
    <div id="conteudo">
        <div class="txtCenter">
            <div class="txtTopo">GERALDO BENEDETE COMPANHIA LTDA</div>
            <div class="text">CNPJ: 45.477.452/0001-05</div>
            <div class="text">AVENIDA GETULIO VARGAS, 339, BAMBU, PORTO FELIZ, SP</div>
        </div>
    </div>
    """

    print("🔍 Extracting data from HTML div elements...")
    print("=" * 50)

    # Extract data using default div ID
    result = extract_div_data(html_content)
    print("📄 Extracted Data:")
    print(result)

    print("\n" + "=" * 50)

    # Example with custom div ID
    custom_html = """
    <div id="company-info">
        <div class="txtTopo">ACME CORPORATION</div>
        <div class="text">CNPJ: 99.999.999/0001-00</div>
        <div class="text">RUA PRINCIPAL, 1000, CENTRO, SAO PAULO, SP</div>
    </div>
    """

    print("🔍 Extracting data from custom div ID...")
    result_custom = extract_div_data(custom_html, div_id="company-info")
    print("📄 Extracted Data:")
    print(result_custom)

    print("\n" + "=" * 50)

    # Example with missing div
    missing_div_html = "<div id='other'>No company data here</div>"
    print("🔍 Testing with missing div...")
    result_missing = extract_div_data(missing_div_html)
    print("📄 Result:")
    print(result_missing)


if __name__ == "__main__":
    main()