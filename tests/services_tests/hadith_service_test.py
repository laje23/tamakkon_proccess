# tests/services_tests/hadith_service_test.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.hadith_service import HadithService

@pytest.fixture
def hadith_service_fixture():
    """
    Fixture برای HadithService:
    - instance از سرویس
    - mock بات‌ها
    - mock مدل دیتابیس
    """
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    mock_db = MagicMock()

    service = HadithService(bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    service.db = mock_db  # جایگزین کردن مدل واقعی با mock
    return service, bale_bot, eitaa_bot, mock_db

@pytest.mark.asyncio
async def test_auto_send_success(hadith_service_fixture):
    """
    تست auto_send وقتی حدیث آماده هست
    """
    service, bale_bot, eitaa_bot, mock_db = hadith_service_fixture

    # mock کردن دیتابیس برای برگردوندن یک حدیث آماده
    mock_db.return_auto_content.return_value = ("متن حدیث تستی", 42)

    # patch کردن process_hadith_message تا روی متن واقعی تاثیر نگذاره
    with patch("services.hadith_service.process_hadith_message", side_effect=lambda c, i, eitaa: f"{c}-{i}-{'eitaa' if eitaa else 'bale'}"):
        response = await service.auto_send()

    # بررسی که send_text صدا زده شده
    bale_bot.send_message.assert_awaited_once()
    eitaa_bot.send_message.assert_awaited_once()

    # بررسی اینکه mark_sent صدا زده شده
    mock_db.mark_sent.assert_called_once_with(42)

    # بررسی خروجی success_response
    assert "حدیث با شناسه 42 ارسال شد" in response["message"]

@pytest.mark.asyncio
async def test_auto_send_no_content(hadith_service_fixture):
    """
    تست auto_send وقتی هیچ حدیث آماده‌ای نیست
    """
    service, _, _, mock_db = hadith_service_fixture
    mock_db.return_auto_content.return_value = None

    response = await service.auto_send()

    # بررسی خروجی error_response
    assert "هیچ حدیثی برای ارسال موجود نیست" in response["message"]
