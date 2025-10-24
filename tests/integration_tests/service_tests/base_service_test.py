import pytest
from unittest.mock import AsyncMock, MagicMock
from services.base_service import BaseService
from config.channels import bale_channel_id, eitaa_channel_id


@pytest.fixture
def mock_bots():
    bale_bot = MagicMock()
    eitaa_bot = MagicMock()

    # متدهای async هر بات -> AsyncMock
    bale_bot.send_message = AsyncMock()
    bale_bot.send_photo = AsyncMock()
    bale_bot.send_video = AsyncMock()
    bale_bot.send_audio = AsyncMock()

    eitaa_bot.send_message = AsyncMock()
    eitaa_bot.send_file = AsyncMock()

    return bale_bot, eitaa_bot


@pytest.mark.asyncio
async def test_send_text_calls_both_bots(mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = BaseService(db_model=None, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    result = await service.send_text("hello bale", "hello eitaa")

    bale_bot.send_message.assert_awaited_once_with(bale_channel_id, "hello bale")
    eitaa_bot.send_message.assert_awaited_once_with(eitaa_channel_id, "hello eitaa")
    assert result["message"] == "پیام متنی ارسال شد"


@pytest.mark.asyncio
async def test_send_media_photo_calls_correct_methods(mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = BaseService(db_model=None, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    result = await service.send_media("photo", "file123", "cap text")

    bale_bot.send_photo.assert_awaited_once_with(bale_channel_id, "file123", "cap text")
    eitaa_bot.send_file.assert_awaited_once_with(eitaa_channel_id, "file123", "cap text")
    assert result["message"] == "photo ارسال شد"


@pytest.mark.asyncio
async def test_send_media_video_calls_correct_methods(mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = BaseService(db_model=None, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    result = await service.send_media("video", "vid123", "video caption")

    bale_bot.send_video.assert_awaited_once_with(bale_channel_id, "vid123", "video caption")
    eitaa_bot.send_file.assert_awaited_once_with(eitaa_channel_id, "vid123", "video caption")
    assert result["message"] == "video ارسال شد"


@pytest.mark.asyncio
async def test_send_media_audio_calls_correct_methods(mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = BaseService(db_model=None, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    result = await service.send_media("audio", "aud123", "audio caption")

    bale_bot.send_audio.assert_awaited_once_with(bale_channel_id, "aud123", "audio caption")
    eitaa_bot.send_file.assert_awaited_once_with(eitaa_channel_id, "aud123", "audio caption")
    assert result["message"] == "audio ارسال شد"


@pytest.mark.asyncio
async def test_send_media_invalid_returns_error(mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = BaseService(db_model=None, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    # وقتی media_type نامعتبر است، safe_run باید error response بدهد
    result = await service.send_media("invalid_type", "file123")

    assert result['success'] is False  
    assert "فرمت فایل نا معتبر" in result["error_message"]
