import os
import pytest
import requests
from unittest.mock import AsyncMock, MagicMock, patch

# Set a dummy token for testing
os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'

# Import modules directly from new structure
from src.extraction import extract_div_data, extract_table_data, create_products_dataframe
from src.scraping import is_url, fetch_webpage_title, fetch_webpage_title_from_html
from src.bot import start, get_dataframe, handle_photo


@pytest.mark.asyncio
async def test_start_handler():
    """Test the /start command handler."""
    # Mock the update and context
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message
    mock_context = MagicMock()

    # Call the handler
    await start(mock_update, mock_context)

    # Verify the response
    mock_message.reply_text.assert_called_once_with(
        'Hi! Send me an image with a QR code, and I\'ll try to decode it.'
    )


@pytest.mark.asyncio
async def test_handle_photo_with_qr_code():
    """Test photo handler when QR code is found."""
    # Create a mock QR code object
    mock_qr_obj = MagicMock()
    mock_qr_obj.data = b"Hello World"

    # Mock the update and context
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    # Mock the image and decode function
    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list
        mock_update.message.photo = [mock_photo]

        # Call the handler
        await handle_photo(mock_update, mock_context)

        # Verify the calls
        mock_context.bot.get_file.assert_called_once_with(mock_photo.file_id)
        mock_file.download_as_bytearray.assert_called_once()
        mock_image_open.assert_called_once()
        mock_decode.assert_called_once_with(mock_image)
        mock_message.reply_text.assert_called_once_with("QR Code found: Hello World")


@pytest.mark.asyncio
async def test_handle_photo_multiple_qr_codes():
    """Test photo handler when multiple QR codes are found."""
    # Create mock QR code objects
    mock_qr_obj1 = MagicMock()
    mock_qr_obj1.data = b"First QR"
    mock_qr_obj2 = MagicMock()
    mock_qr_obj2.data = b"Second QR"

    # Mock the update and context
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    # Mock the image and decode function
    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj1, mock_qr_obj2]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list
        mock_update.message.photo = [mock_photo]

        # Call the handler
        await handle_photo(mock_update, mock_context)

        # Verify the calls
        assert mock_message.reply_text.call_count == 2
        mock_message.reply_text.assert_any_call("QR Code found: First QR")
        mock_message.reply_text.assert_any_call("QR Code found: Second QR")


@pytest.mark.asyncio
async def test_handle_photo_no_qr_code():
    """Test photo handler when no QR code is found."""
    # Mock the update and context
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    # Mock the image and decode function (no QR codes found)
    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list
        mock_update.message.photo = [mock_photo]

        # Call the handler
        await handle_photo(mock_update, mock_context)

        # Verify the response
        mock_message.reply_text.assert_called_once_with("No QR code found in the image.")


@pytest.mark.asyncio
async def test_handle_photo_uses_highest_resolution():
    """Test that the handler uses the highest resolution photo."""
    # Mock the update and context
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    # Create multiple photos (different resolutions)
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
    """Test photo handler when QR code contains a URL."""
    # Create a mock QR code object with URL
    mock_qr_obj = MagicMock()
    mock_qr_obj.data = b"https://example.com"

    # Mock the update and context
    mock_update = MagicMock()
    mock_message = MagicMock()
    mock_message.reply_text = AsyncMock()
    mock_update.message = mock_message

    mock_photo = MagicMock()
    mock_file = AsyncMock()
    mock_context = MagicMock()
    mock_context.bot.get_file = AsyncMock(return_value=mock_file)
    mock_file.download_as_bytearray = AsyncMock(return_value=b"fake_image_data")

    # Mock the image, decode, requests, and fetch functions
    with patch('PIL.Image.open') as mock_image_open, \
         patch('pyzbar.pyzbar.decode', return_value=[mock_qr_obj]) as mock_decode, \
         patch('src.scraping.web_scraping.requests.get') as mock_requests_get, \
         patch('src.scraping.web_scraping.fetch_webpage_title_from_html', return_value='📄 Title: Test') as mock_fetch:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Mock the response
        mock_response = MagicMock()
        mock_response.content = b'<html><body>Test</body></html>'
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response

        # Set up the photo list
        mock_update.message.photo = [mock_photo]

        # Call the handler
        await handle_photo(mock_update, mock_context)

        # Verify the calls
        assert mock_message.reply_text.call_count >= 1
        calls = mock_message.reply_text.call_args_list
        assert any('https://example.com' in str(call) for call in calls)


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
    html_content = b'''
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
