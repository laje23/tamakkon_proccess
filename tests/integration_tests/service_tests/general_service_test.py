import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.general_service import GeneralService
from utils.datetime import get_mentioning_day

@pytest.fixture
def mock_bots_and_model():
    bale_bot = MagicMock()
    eitaa_bot = MagicMock()
    bale_bot.send_audio = AsyncMock()
    bale_bot.send_photo = AsyncMock()
    bale_bot.send_message = AsyncMock()
    bale_bot.send_video = AsyncMock()

    eitaa_bot.send_file = AsyncMock()
    eitaa_bot.send_message = AsyncMock()

    audio_model = MagicMock()
    return bale_bot, eitaa_bot, audio_model


@pytest.mark.asyncio
@patch("services.general_service.file_id_to_bynery", new_callable=AsyncMock)
async def test_send_audio_file(mock_file, mock_bots_and_model):
    bale_bot, eitaa_bot, audio_model = mock_bots_and_model
    service = GeneralService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot, audio_model=audio_model)

    bin_mock = AsyncMock()
    bin_mock.read.return_value = b"binary_audio"
    mock_file.return_value = bin_mock

    result = await service.send_audio_file("file123", "caption text")

    mock_file.assert_awaited_once_with("file123", service.bale_bot)
    bale_bot.send_audio.assert_awaited_once_with(service.bale_channel_id, b"binary_audio", "caption text")
    eitaa_bot.send_file.assert_awaited_once_with(service.eitaa_channel_id, bin_mock, "caption text")
    assert result["message"] == "فایل صوتی ارسال شد"


@pytest.mark.asyncio
async def test_send_photo_with_text(mock_bots_and_model):
    bale_bot, eitaa_bot, _ = mock_bots_and_model
    service = GeneralService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    result = await service.send_photo_with_text("photo.png", "my text")

    bale_bot.send_photo.assert_awaited_once_with(service.bale_channel_id, "photo.png", "my text")
    eitaa_bot.send_file.assert_awaited_once_with(service.eitaa_channel_id, "photo.png", "my text")
    assert result["message"] == "پیام تصویری ارسال شد"


@pytest.mark.asyncio
async def test_send_text_message(mock_bots_and_model):
    bale_bot, eitaa_bot, _ = mock_bots_and_model
    service = GeneralService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    result = await service.send_text_message("hello world")

    bale_bot.send_message.assert_awaited_once_with(service.bale_channel_id, "hello world")
    eitaa_bot.send_message.assert_awaited_once_with(service.eitaa_channel_id, "hello world")
    assert result["message"] == "پیام متنی ارسال شد"


@pytest.mark.asyncio
@patch("services.general_service.GeneralService.send_audio_file", new_callable=AsyncMock)
async def test_send_prayer(mock_send_audio, mock_bots_and_model):
    bale_bot, eitaa_bot, audio_model = mock_bots_and_model
    service = GeneralService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot, audio_model=audio_model)

    audio_model.get_file_id_and_caption_by_id.return_value = ("file123", "caption123")
    mock_send_audio.return_value = {"success": True, "message": "فایل صوتی ارسال شد"}

    result = await service.send_prayer("faraj")

    audio_model.get_file_id_and_caption_by_id.assert_called_once_with(1)
    mock_send_audio.assert_awaited_once_with("file123", "caption123")
    assert result["message"] == "دعا ارسال شد"


@pytest.mark.asyncio
@patch("services.general_service.get_mentioning_day")
@patch("services.general_service.GeneralService.send_photo_with_text", new_callable=AsyncMock)
async def test_send_day_info(mock_send_photo, mock_get_day, mock_bots_and_model):
    bale_bot, eitaa_bot, _ = mock_bots_and_model
    service = GeneralService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    mock_get_day.return_value = {
        "name": "دوشنبه",
        "date": "1404/08/10",
        "zekr": "اذکار روز",
        "path": "path/to/photo.png"
    }
    mock_send_photo.return_value = {"success": True, "message": "پیام تصویری ارسال شد"}

    result = await service.send_day_info()

    mock_get_day.assert_called_once()
    mock_send_photo.assert_awaited_once()
    assert result["message"] == "اطلاعات روز ارسال شد "


@pytest.mark.asyncio
@patch("services.general_service.get_media_bytes", new_callable=AsyncMock)
async def test_send_message_to_channel_photo(mock_get_media_bytes, mock_bots_and_model):
    bale_bot, eitaa_bot, _ = mock_bots_and_model
    service = GeneralService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    media_msg = MagicMock()
    media_msg.caption = "photo caption"
    media_msg.text = None
    mock_get_media_bytes.return_value = (b"binary", "photo")

    result = await service.send_message_to_channel(media_msg, bale_bot)

    mock_get_media_bytes.assert_awaited_once_with(media_msg, bale_bot)
    bale_bot.send_photo.assert_awaited_once_with(service.bale_channel_id, b"binary", "photo caption")
    eitaa_bot.send_file.assert_awaited_once_with(service.eitaa_channel_id, b"binary", "photo caption")
    assert result["message"] == "پیام ارسال شد"


@pytest.mark.asyncio
async def test_save_new_audio_success(mock_bots_and_model):
    bale_bot, eitaa_bot, audio_model = mock_bots_and_model
    user_temp_data = {123: {"audio_id": 1}}
    service = GeneralService(user_temp_data=user_temp_data, bale_bot=bale_bot, eitaa_bot=eitaa_bot, audio_model=audio_model)

    message = MagicMock()
    message.author.id = 123
    message.document.id = "file123"
    message.caption = "new caption"
    message.chat.id = 456

    await service.save_new_audio(message)

    audio_model.update_row_by_id.assert_called_once_with(1, "file123", "new caption")
    bale_bot.send_message.assert_awaited_once()
    assert 123 not in service.user_temp_data
