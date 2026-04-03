import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Set a dummy token for testing
os.environ['TELEGRAM_BOT_TOKEN'] = 'dummy_token_for_testing'

import main


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
    await main.start(mock_update, mock_context)

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
    with patch('main.Image.open') as mock_image_open, \
         patch('main.decode', return_value=[mock_qr_obj]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list
        mock_update.message.photo = [mock_photo]

        # Call the handler
        await main.handle_photo(mock_update, mock_context)

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
    with patch('main.Image.open') as mock_image_open, \
         patch('main.decode', return_value=[mock_qr_obj1, mock_qr_obj2]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list
        mock_update.message.photo = [mock_photo]

        # Call the handler
        await main.handle_photo(mock_update, mock_context)

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
    with patch('main.Image.open') as mock_image_open, \
         patch('main.decode', return_value=[]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list
        mock_update.message.photo = [mock_photo]

        # Call the handler
        await main.handle_photo(mock_update, mock_context)

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
    with patch('main.Image.open') as mock_image_open, \
         patch('main.decode', return_value=[]) as mock_decode:

        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Set up the photo list (low res first, high res last)
        mock_update.message.photo = [mock_photo_low, mock_photo_high]

        # Call the handler
        await main.handle_photo(mock_update, mock_context)

        # Verify it uses the last (highest resolution) photo
        mock_context.bot.get_file.assert_called_once_with(mock_photo_high.file_id)
