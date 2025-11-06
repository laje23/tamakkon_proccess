import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.hadith_service import HadithService
from utils.response import success_response, error_response

@pytest.fixture
def mock_bots():
    bale_bot = MagicMock()
    eitaa_bot = MagicMock()
    bale_bot.send_message = AsyncMock()
    eitaa_bot.send_message = AsyncMock()
    return bale_bot, eitaa_bot

@pytest.mark.asyncio
@patch("services.hadith_service.process_hadith_message")
async def test_auto_send_success(mock_process, mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = HadithService(bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    # ماک دیتابیس
    content = "متن حدیث"
    hadith_id = 123
    service.db.return_auto_content = MagicMock(return_value=(content, hadith_id))
    service.db.mark_sent = MagicMock()

    # ماک process_hadith_message
    mock_process.side_effect = lambda c, i, eitaa: f"text_{'eitaa' if eitaa else 'bale'}"

    # ماک send_text
    service.send_text = AsyncMock()

    result = await service.auto_send()

    service.db.return_auto_content.assert_called_once()
    mock_process.assert_any_call(content, hadith_id, eitaa=False)
    mock_process.assert_any_call(content, hadith_id, eitaa=True)
    service.send_text.assert_awaited_once_with("text_bale", "text_eitaa")
    service.db.mark_sent.assert_called_once_with(hadith_id)

    assert result["message"] == f"حدیث با شناسه {hadith_id} ارسال شد"

@pytest.mark.asyncio
async def test_auto_send_no_content(mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = HadithService(bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    # دیتابیس هیچ چیزی برای ارسال ندارد
    service.db.return_auto_content = MagicMock(return_value=None)

    result = await service.auto_send()

    service.db.return_auto_content.assert_called_once()
    assert result["message"] == "هیچ حدیثی برای ارسال موجود نیست"
    assert result["success"] is False
