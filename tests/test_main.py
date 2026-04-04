import os
import pytest
import requests
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Set a dummy token for testing
os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'

# Import modules from src
from src.extraction.data_extraction import (
    extract_div_data,
    extract_company_info,
    extract_table_data,
    extract_total_data,
    extract_emission_info,
)
from src.extraction.data_processing import create_products_dataframe
from src.scraping.web_scraping import is_url, is_sefaz_url, fetch_webpage_title, fetch_webpage_title_from_html
from src.bot.handlers import start, help_command, last_scan, list_scans, detail_scan, handle_photo
from src.data import store as data_store


@pytest.mark.asyncio
async def test_start_handler():
    """Test the /start command handler."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()

    await start(mock_update, mock_context)

    mock_message.reply_text.assert_called_once()
    call_text = mock_message.reply_text.call_args[0][0]
    assert '/help' in call_text


@pytest.mark.asyncio
async def test_help_command():
    """Test the /help command lists all commands."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()

    await help_command(mock_update, mock_context)

    mock_message.reply_text.assert_called_once()
    reply = mock_message.reply_text.call_args[0][0]
    for cmd in ['/start', '/help', '/last', '/scans', '/detail']:
        assert cmd in reply


@pytest.mark.asyncio
async def test_handle_photo_with_qr_code():
    """Test photo handler when QR code text (non-Sefaz) is found — returns 'No Sefaz link found'."""
    mock_qr_obj = MagicMock()
    mock_qr_obj.data = b"Hello World"

    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj]):

        mock_image_open.return_value = MagicMock()
        mock_update.message.photo = [mock_photo]

        await handle_photo(mock_update, mock_context)

        mock_message.reply_text.assert_called_once_with("No Sefaz link found.")


@pytest.mark.asyncio
async def test_handle_photo_multiple_qr_codes():
    """Test photo handler processes only the first QR code."""
    mock_qr_obj1 = MagicMock()
    mock_qr_obj1.data = b"First QR"
    mock_qr_obj2 = MagicMock()
    mock_qr_obj2.data = b"Second QR"

    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj1, mock_qr_obj2]):

        mock_image_open.return_value = MagicMock()
        mock_update.message.photo = [mock_photo]

        await handle_photo(mock_update, mock_context)

        # Only one reply because only first QR is processed and it's not a Sefaz URL
        mock_message.reply_text.assert_called_once_with("No Sefaz link found.")


@pytest.mark.asyncio
async def test_handle_photo_no_qr_code():
    """Test photo handler when no QR code is found."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[]):

        mock_image_open.return_value = MagicMock()
        mock_update.message.photo = [mock_photo]

        await handle_photo(mock_update, mock_context)

        mock_message.reply_text.assert_called_once_with("No QR Code Found.")


@pytest.mark.asyncio
async def test_handle_photo_uses_highest_resolution():
    """Test that the handler uses the highest resolution photo."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo_low = MagicMock()
    mock_photo_high = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    # Mock the image and decode function
    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list (low res first, high res last)
        mock_update.message.photo = [mock_photo_low, mock_photo_high]

        # Call the handler
        await handle_photo(mock_update, mock_context)

        # Verify it uses the last (highest resolution) photo
        mock_context.bot.get_file.assert_called_once_with(mock_photo_high.file_id)


def test_is_url_valid():
    """Test URL detection with valid URLs."""
    valid_urls = [
        'https://www.example.com',
        'http://example.com',
        'https://github.com/user/repo',
        'http://localhost:8000/path'
    ]
    for url in valid_urls:
        assert is_url(url) is True


def test_is_url_invalid():
    """Test URL detection with invalid URLs."""
    invalid_urls = [
        'Hello World',
        'not a url',
        'www.example.com',  # Missing scheme
        'just some text',
        ''
    ]
    for url in invalid_urls:
        assert is_url(url) is False


@pytest.mark.asyncio
async def test_fetch_webpage_title_success():
    """Test fetching webpage title successfully."""
    mock_response = MagicMock()
    mock_response.content = b'<html><head><title>Test Page</title><meta name="description" content="Test Description"></head><body><p>First paragraph text</p></body></html>'
    
    with patch('src.scraping.web_scraping.requests.get', return_value=mock_response) as mock_get:
        result = await fetch_webpage_title('https://example.com')
        
        mock_get.assert_called_once()
        assert 'Test Page' in result
        assert 'Test Description' in result


@pytest.mark.asyncio
async def test_fetch_webpage_title_timeout():
    """Test handling of timeout error."""
    with patch('src.scraping.web_scraping.requests.get', side_effect=requests.exceptions.Timeout()):
        result = await fetch_webpage_title('https://example.com')
        
        assert 'timed out' in result.lower()


@pytest.mark.asyncio
async def test_fetch_webpage_title_connection_error():
    """Test handling of connection error."""
    with patch('src.scraping.web_scraping.requests.get', side_effect=requests.exceptions.ConnectionError()):
        result = await fetch_webpage_title('https://example.com')
        
        assert 'could not connect' in result.lower()


@pytest.mark.asyncio
async def test_handle_photo_with_url_in_qr():
    """Test photo handler when QR code contains a non-Sefaz URL — returns 'No Sefaz link found'."""
    mock_qr_obj = MagicMock()
    mock_qr_obj.data = b"https://example.com"

    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj]):

        mock_image_open.return_value = MagicMock()
        mock_update.message.photo = [mock_photo]

        await handle_photo(mock_update, mock_context)

        mock_message.reply_text.assert_called_once_with("No Sefaz link found.")


@pytest.mark.asyncio
async def test_handle_photo_sefaz_success():
    """Test full success path with a valid Sefaz URL QR code."""
    mock_qr_obj = MagicMock()
    mock_qr_obj.data = b"https://nfce.fazenda.sp.gov.br/NFCeConsultaPublica?chNFe=123"

    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    mock_response = MagicMock()
    mock_response.content = b'<html><body></body></html>'
    mock_response.raise_for_status = MagicMock()

    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj]), \
         patch('src.bot.handlers.requests.get', return_value=mock_response), \
         patch('src.bot.handlers.extract_company_info', return_value={'company_name': 'ACME', 'cnpj': '12.345.678/0001-90'}), \
         patch('src.bot.handlers.extract_table_data', return_value=[{'Produto': 'Item', 'Qtde': 1, 'Vl_Total': 5.0}]), \
         patch('src.bot.handlers.extract_total_data', return_value={'total_items': 1, 'amount_paid': 5.0, 'payment_method': 'PIX'}), \
         patch('src.bot.handlers.extract_emission_info', return_value={'emission_date': '01/01/2026 10:00:00', 'access_key': '35260312495021000104650010000020351469425812'}), \
         patch('src.bot.handlers.next_scan_id', return_value=42), \
         patch('src.bot.handlers.save_scan_to_csv') as mock_csv, \
         patch('src.bot.handlers.save_scan_to_json') as mock_json:

        mock_image_open.return_value = MagicMock()
        mock_update.message.photo = [mock_photo]

        await handle_photo(mock_update, mock_context)

        mock_csv.assert_called_once()
        # Verify ID and access key are passed to CSV
        csv_call_args = mock_csv.call_args[0]
        assert csv_call_args[0] == 42  # scan_id
        assert csv_call_args[6] == '35260312495021000104650010000020351469425812'  # access_key
        mock_json.assert_called_once()
        saved_payload = mock_json.call_args[0][0]
        assert saved_payload['id'] == 42
        assert saved_payload['access_key'] == '35260312495021000104650010000020351469425812'
        mock_message.reply_text.assert_called_once()
        reply_text = mock_message.reply_text.call_args[0][0]
        assert 'Receipt scanned successfully' in reply_text
        assert 'ACME' in reply_text
        assert 'PIX' in reply_text


@pytest.mark.asyncio
async def test_handle_photo_sefaz_site_down():
    """Test photo handler when Sefaz site is unreachable."""
    mock_qr_obj = MagicMock()
    mock_qr_obj.data = b"https://nfce.fazenda.sp.gov.br/consulta"

    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj]), \
         patch('src.bot.handlers.requests.get', side_effect=requests.exceptions.ConnectionError()):

        mock_image_open.return_value = MagicMock()
        mock_update.message.photo = [mock_photo]

        await handle_photo(mock_update, mock_context)

        mock_message.reply_text.assert_called_once_with("Sefaz site is down.")


@pytest.mark.asyncio
async def test_handle_photo_data_bad_formatted():
    """Test photo handler when extraction yields no usable data."""
    mock_qr_obj = MagicMock()
    mock_qr_obj.data = b"https://nfce.fazenda.sp.gov.br/consulta"

    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    mock_response = MagicMock()
    mock_response.content = b'<html><body></body></html>'
    mock_response.raise_for_status = MagicMock()

    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj]), \
         patch('src.bot.handlers.requests.get', return_value=mock_response), \
         patch('src.bot.handlers.extract_company_info', return_value={'company_name': '', 'cnpj': ''}), \
         patch('src.bot.handlers.extract_table_data', return_value=[]), \
         patch('src.bot.handlers.extract_total_data', return_value={}), \
         patch('src.bot.handlers.extract_emission_info', return_value={}):

        mock_image_open.return_value = MagicMock()
        mock_update.message.photo = [mock_photo]

        await handle_photo(mock_update, mock_context)

        mock_message.reply_text.assert_called_once_with("Data bad formatted.")


def test_is_sefaz_url_valid():
    """Test that Sefaz portal URLs are correctly identified."""
    valid_sefaz_urls = [
        'https://nfce.fazenda.sp.gov.br/NFCeConsultaPublica',
        'http://www.sefaz.ba.gov.br/nfe',
        'https://www.nfce.fazenda.pr.gov.br/nfce/consulta',
    ]
    for url in valid_sefaz_urls:
        assert is_sefaz_url(url) is True


def test_is_sefaz_url_invalid():
    """Test that non-Sefaz URLs are rejected."""
    non_sefaz_urls = [
        'https://www.example.com',
        'https://google.com',
        'https://github.com',
        '',
    ]
    for url in non_sefaz_urls:
        assert is_sefaz_url(url) is False


def test_extract_company_info_success():
    """Test extracting company name and CNPJ from HTML."""
    html_content = '''
    <div id="conteudo">
        <div class="txtTopo">ACME SUPERMERCADO LTDA</div>
        <div class="text">CNPJ: 12.345.678/0001-90 Inscrição Estadual: 111222333444</div>
    </div>
    '''
    result = extract_company_info(html_content)
    assert result['company_name'] == 'ACME SUPERMERCADO LTDA'
    assert result['cnpj'] == '12.345.678/0001-90'


def test_extract_company_info_missing_div():
    """Test extract_company_info when div is not found."""
    result = extract_company_info('<div id="other">nothing</div>')
    assert result == {'company_name': '', 'cnpj': ''}


@pytest.mark.asyncio
async def test_last_scan_no_data():
    """Test /last when no scans have been recorded."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()

    with patch('src.bot.handlers.get_last_scan_from_csv', return_value=None):
        await last_scan(mock_update, mock_context)

    mock_message.reply_text.assert_called_once()
    assert 'No scans recorded' in mock_message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_last_scan_with_data():
    """Test /last returns formatted receipt data."""
    mock_row = {
        'Date': '01/04/2026 10:00:00',
        'Company Name': 'ACME STORE',
        'CNPJ': '12.345.678/0001-90',
        'Amount Paid': '49.90',
        'Payment Method': 'PIX',
    }
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()

    with patch('src.bot.handlers.get_last_scan_from_csv', return_value=mock_row):
        await last_scan(mock_update, mock_context)

    reply = mock_message.reply_text.call_args[0][0]
    assert 'ACME STORE' in reply
    assert '12.345.678/0001-90' in reply
    assert 'PIX' in reply


def test_get_last_scan_from_headerless_csv(tmp_path):
    """Test reading the last row from a legacy CSV file without headers."""
    csv_file = tmp_path / 'scans.csv'
    csv_file.write_text(
        '27/03/2026 13:08:49,MATEUS DE CAMPOS PORTO FELIZ - ME,12.495.021/0001-04,67.04,Cartão de Crédito\n'
        '29/03/2026 11:09:00,GERALDO BENEDETE COMPANHIA LTDA,45.477.452/0001-05,5.79,Cartão de Crédito\n',
        encoding='utf-8',
    )

    with patch.object(data_store, 'CSV_FILE', csv_file):
        row = data_store.get_last_scan_from_csv()

    assert row is not None
    assert row['Date'] == '29/03/2026 11:09:00'
    assert row['Company Name'] == 'GERALDO BENEDETE COMPANHIA LTDA'
    assert row['CNPJ'] == '45.477.452/0001-05'
    assert row['Amount Paid'] == '5.79'
    assert row['Payment Method'] == 'Cartão de Crédito'


def test_get_all_scans_from_headerless_csv(tmp_path):
    """Test reading all rows from a legacy CSV file without headers."""
    csv_file = tmp_path / 'scans.csv'
    csv_file.write_text(
        '27/03/2026 13:08:49,MATEUS DE CAMPOS PORTO FELIZ - ME,12.495.021/0001-04,67.04,Cartão de Crédito\n'
        '29/03/2026 11:09:00,GERALDO BENEDETE COMPANHIA LTDA,45.477.452/0001-05,5.79,Cartão de Crédito\n',
        encoding='utf-8',
    )

    with patch.object(data_store, 'CSV_FILE', csv_file):
        rows = data_store.get_all_scans_from_csv()

    assert len(rows) == 2
    assert rows[0]['Company Name'] == 'MATEUS DE CAMPOS PORTO FELIZ - ME'
    assert rows[1]['Company Name'] == 'GERALDO BENEDETE COMPANHIA LTDA'


def test_extract_div_data_success():
    """Test extracting data from div elements."""
    html_content = '''
    <div id="conteudo">
        <div class="txtCenter">
            <div class="txtTopo">GERALDO BENEDETE COMPANHIA LTDA</div>
            <div class="text">CNPJ: 45.477.452/0001-05</div>
            <div class="text">AVENIDA GETULIO VARGAS, 339, BAMBU, PORTO FELIZ, SP</div>
        </div>
    </div>
    '''
    result = extract_div_data(html_content)
    assert 'GERALDO BENEDETE COMPANHIA LTDA' in result
    assert 'CNPJ' in result
    assert '45.477.452/0001-05' in result
    assert 'AVENIDA GETULIO VARGAS' in result


def test_extract_div_data_custom_div_id():
    """Test extracting data with custom div ID."""
    html_content = '''
    <div id="custom_div">
        <div class="txtTopo">COMPANY NAME</div>
        <div class="text">CNPJ: 12.345.678/0001-90</div>
    </div>
    '''
    result = extract_div_data(html_content, div_id='custom_div')
    assert 'COMPANY NAME' in result
    assert '12.345.678/0001-90' in result


def test_extract_div_data_not_found():
    """Test extracting data when div is not found."""
    html_content = '<div id="other"><p>Test</p></div>'
    result = extract_div_data(html_content)
    assert 'not found' in result.lower()


def test_extract_div_data_formatting():
    """Test that div data is formatted with proper icons."""
    html_content = '''
    <div id="conteudo">
        <div class="txtTopo">TEST CO</div>
        <div class="text">CNPJ: 11.111.111/0001-11</div>
        <div class="text">AVENIDA TEST, 123</div>
    </div>
    '''
    result = extract_div_data(html_content)
    assert '🏢' in result  # Company icon
    assert '📋' in result  # CNPJ icon
    assert '📍' in result  # Address icon


@pytest.mark.asyncio
async def test_fetch_webpage_title_with_div_extraction():
    """Test that fetch_webpage_title includes div data extraction."""
    html_content = '''
    <html>
    <head><title>Test Page</title>
    <meta name="description" content="Test description">
    </head>
    <body>
    <p>This is the first paragraph.</p>
    <div id="conteudo">
        <div class="txtTopo">COMPANY FROM WEB</div>
        <div class="text">CNPJ: 11.222.333/0001-44</div>
    </div>
    </body>
    </html>
    '''

    with patch('src.scraping.web_scraping.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.content = html_content
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = await fetch_webpage_title('https://example.com')

        # Check that regular webpage info is included
        assert '📄 Title: Test Page' in result
        assert '📝 Description: Test description' in result
        assert 'This is the first paragraph' in result

        # Check that div data is also included
        assert '🏢 Company: COMPANY FROM WEB' in result
        assert '📋 CNPJ: 11.222.333/0001-44' in result


def test_extract_table_data_success():
    """Test extracting table data from HTML."""
    html_content = '''
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
    </table>
    '''
    result = extract_table_data(html_content)
    assert len(result) == 1
    product = result[0]
    assert product['Produto'] == 'CREME LEITE NESTLE TP 200G'
    assert product['Código'] == '12332'
    assert product['Qtde'] == 1
    assert product['UN'] == 'UN0001'
    assert product['Vl_Unit'] == 5.79
    assert product['Vl_Total'] == 5.79


def test_extract_table_data_no_table():
    """Test extracting table data when no table is found."""
    html_content = '<div>No table here</div>'
    result = extract_table_data(html_content)
    assert result == []


def test_create_products_dataframe():
    """Test creating pandas DataFrame from table data."""
    table_data = [
        {
            'Produto': 'Test Product',
            'Código': '12345',
            'Qtde': 2,
            'UN': 'UN001',
            'Vl_Unit': 10.50,
            'Vl_Total': 21.00
        }
    ]
    df = create_products_dataframe(table_data)
    assert len(df) == 1
    assert df.iloc[0]['Produto'] == 'Test Product'
    assert df.iloc[0]['Vl_Total'] == 21.00


def test_create_products_dataframe_empty():
    """Test creating DataFrame from empty data."""
    df = create_products_dataframe([])
    assert df.empty


def test_extract_total_data_success():
    """Test extracting total payment data from HTML."""
    html_content = '''
    <div id="totalNota" class="txtRight">
      <div id="linhaTotal">
        <label>Qtd. total de itens:</label>
        <span class="totalNumb">1</span>
      </div>
      <div id="linhaTotal" class="linhaShade">
        <label>Valor a pagar R$:</label>
        <span class="totalNumb txtMax">5,79</span>
      </div>
      <div id="linhaForma">
        <label>Forma de pagamento:</label>
        <span class="totalNumb txtTitR">Valor pago R$:</span>
      </div>
      <div id="linhaTotal">
        <label class="tx">
            Cartão de Crédito
        </label>
        <span class="totalNumb">5,79</span>
      </div>
      <div id="linhaTotal">
        <label class="tx">Troco </label>
        <span class="totalNumb">0,00</span>
      </div>
    </div>
    '''
    result = extract_total_data(html_content)
    assert result['total_items'] == 1
    assert result['amount_to_pay'] == 5.79
    assert result['payment_method'] == 'Cartão de Crédito'
    assert result['amount_paid'] == 5.79
    assert result['change'] == 0.00


def test_extract_total_data_no_div():
    """Test extracting total data when div is not found."""
    html_content = '<div id="other"><p>Test</p></div>'
    result = extract_total_data(html_content)
    assert result == {}


def test_extract_emission_info_success():
    """Test extracting emission information from HTML."""
    html_content = '''
    <div id="infos" class="txtCenter">
      <div data-role="collapsible" data-collapsed-icon="carat-d" data-expanded-icon="carat-u" data-collapsed="false">
        <h4>Informações gerais da Nota</h4>
        <ul data-role="listview" data-inset="false">
          <li>
            <strong>EMISSÃO NORMAL</strong>
            <br>
            <br>
            <strong>Número: </strong>28725<strong> Série: </strong>54<strong> Emissão: </strong>29/03/2026 11:09:00
            - Via Consumidor
            <br><br><strong>Protocolo de Autorização: </strong>135262105954781       29/03/2026 11:09:33<br><br><strong>
              Ambiente de Produção -
              Versão XML:
              4.00
              - Versão XSLT: 2.05
                        </strong>
                        <br><span class="chave">3526 0312 4950 2100 0104 6500 1000 0020 3514 6942 5812</span></li>
        </ul>
      </div>
    </div>
    '''
    result = extract_emission_info(html_content)
    assert result['emission_date'] == '29/03/2026 11:09:00'
    assert result['authorization_protocol'] == '135262105954781'
    assert result['environment'] == 'Produção'
    assert result['access_key'] == '35260312495021000104650010000020351469425812'


def test_extract_emission_info_no_div():
    """Test extracting emission info when div is not found."""
    html_content = '<div id="other"><p>Test</p></div>'
    result = extract_emission_info(html_content)
    assert result == {}


@pytest.mark.asyncio
async def test_list_scans_no_data():
    """Test /scans when no records exist."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()

    with patch('src.bot.handlers.get_all_scans_from_csv', return_value=[]):
        await list_scans(mock_update, mock_context)

    mock_message.reply_text.assert_called_once()
    assert 'No scans recorded' in mock_message.reply_text.call_args[0][0]


@pytest.mark.asyncio
async def test_list_scans_with_data():
    """Test /scans returns a monospace table with all rows."""
    mock_rows = [
        {'ID': '1', 'Date': '01/04/2026 10:00:00', 'Company Name': 'ACME STORE', 'CNPJ': '12.345.678/0001-90', 'Amount Paid': '49.90', 'Payment Method': 'PIX', 'Access Key': ''},
        {'ID': '2', 'Date': '02/04/2026 15:30:00', 'Company Name': 'BETA MARKET', 'CNPJ': '98.765.432/0001-11', 'Amount Paid': '120.50', 'Payment Method': 'Cartão', 'Access Key': ''},
    ]
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()

    with patch('src.bot.handlers.get_all_scans_from_csv', return_value=mock_rows):
        await list_scans(mock_update, mock_context)

    mock_message.reply_text.assert_called_once()
    reply = mock_message.reply_text.call_args[0][0]
    assert 'ACME STORE' in reply
    assert 'BETA MARKET' in reply
    assert '49.90' in reply
    assert '120.50' in reply
    assert 'PIX' in reply


@pytest.mark.asyncio
async def test_detail_scan_no_args():
    """Test /detail with no arguments returns usage hint."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()
    mock_context.args = []

    await detail_scan(mock_update, mock_context)

    reply = mock_message.reply_text.call_args[0][0]
    assert 'Usage' in reply


@pytest.mark.asyncio
async def test_detail_scan_not_found():
    """Test /detail when ID does not exist in JSON."""
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()
    mock_context.args = ['99']

    with patch('src.bot.handlers.get_scan_detail_from_json', return_value=None):
        await detail_scan(mock_update, mock_context)

    reply = mock_message.reply_text.call_args[0][0]
    assert 'No scan found' in reply


@pytest.mark.asyncio
async def test_detail_scan_found():
    """Test /detail returns formatted scan detail."""
    mock_record = {
        'id': 3,
        'emission_date': '01/04/2026 10:00:00',
        'company_name': 'ACME STORE',
        'cnpj': '12.345.678/0001-90',
        'access_key': '35260312495021000104650010000020351469425812',
        'amount_paid': 49.90,
        'payment_method': 'PIX',
        'total_items': 2,
        'items': [
            {'Produto': 'LEITE', 'Código': '111', 'Qtde': 1, 'UN': 'UN', 'Vl_Unit': 5.0, 'Vl_Total': 5.0},
            {'Produto': 'PÃO', 'Código': '222', 'Qtde': 2, 'UN': 'UN', 'Vl_Unit': 3.0, 'Vl_Total': 6.0},
        ],
    }
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()
    mock_context.args = ['3']

    with patch('src.bot.handlers.get_scan_detail_from_json', return_value=mock_record):
        await detail_scan(mock_update, mock_context)

    reply = mock_message.reply_text.call_args[0][0]
    assert 'Scan #3' in reply
    assert 'ACME STORE' in reply
    assert '35260312495021000104650010000020351469425812' in reply
    assert 'LEITE' in reply
    assert 'PIX' in reply


def test_save_and_retrieve_scan_id(tmp_path):
    """Test that scan ID is persisted in CSV and retrieved as expected."""
    csv_file = tmp_path / 'scans.csv'
    json_file = tmp_path / 'scans.json'

    with patch.object(data_store, 'CSV_FILE', csv_file), \
         patch.object(data_store, 'JSON_FILE', json_file):

        assert data_store.next_scan_id() == 1
        data_store.save_scan_to_csv(1, '01/04/2026 10:00:00', 'ACME', '12.345.678/0001-90', 49.90, 'PIX', 'ABC123')
        assert data_store.next_scan_id() == 2
        data_store.save_scan_to_csv(2, '02/04/2026 11:00:00', 'BETA', '98.765.432/0001-11', 12.00, 'Dinheiro', 'DEF456')
        assert data_store.next_scan_id() == 3

        rows = data_store.get_all_scans_from_csv()
        assert len(rows) == 2
        assert rows[0]['ID'] == '1'
        assert rows[0]['Access Key'] == 'ABC123'
        assert rows[1]['ID'] == '2'


def test_get_scan_detail_from_json(tmp_path):
    """Test retrieving a scan record from JSON by ID."""
    json_file = tmp_path / 'scans.json'
    records = [
        {'id': 1, 'company_name': 'ACME', 'amount_paid': 10.0, 'items': []},
        {'id': 2, 'company_name': 'BETA', 'amount_paid': 20.0, 'items': []},
    ]
    json_file.write_text(__import__('json').dumps(records), encoding='utf-8')

    with patch.object(data_store, 'JSON_FILE', json_file):
        result = data_store.get_scan_detail_from_json(2)
        assert result is not None
        assert result['company_name'] == 'BETA'

        missing = data_store.get_scan_detail_from_json(99)
        assert missing is None
