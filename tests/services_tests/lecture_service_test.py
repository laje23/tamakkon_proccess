# tests/services_tests/lecture_service_test.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.lecture_service import LectureService

@pytest.fixture
def lecture_service_fixture():
    """
    Fixture برای LectureService:
    - instance از سرویس
    - mock بات‌ها
    - mock مدل دیتابیس
    """
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    mock_db = MagicMock()

    service = LectureService(bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    service.db = mock_db  # جایگزینی مدل واقعی با mock
    return service, bale_bot, eitaa_bot, mock_db

@pytest.mark.asyncio
async def test_auto_send_success(lecture_service_fixture):
    """
    تست auto_send وقتی سخنرانی آماده است
    """
    service, bale_bot, eitaa_bot, mock_db = lecture_service_fixture

    # mock کردن دیتابیس برای برگردوندن یک lecture آماده
    mock_db.auto_return_lecture.return_value = (7, "file_id_1", "کپشن تستی")

    # patch کردن file_id_to_bynry تا باینری جعلی برگردونه
    with patch("services.lecture_service.file_id_to_bynry", new=AsyncMock(return_value=b"fake_bytes")):
        # patch کردن send_media برای جلوگیری از ارسال واقعی
        service.send_media = AsyncMock()
        response = await service.auto_send()

        # بررسی اینکه send_media await شده
        service.send_media.assert_awaited_once()

    # بررسی اینکه mark_lecture_sent صدا زده شده
    mock_db.mark_lecture_sent.assert_called_once_with(7)

    # بررسی خروجی success_response
    assert "سخنرانی با شناسه 7 ارسال شد" in response["message"]

@pytest.mark.asyncio
async def test_auto_send_no_lecture(lecture_service_fixture):
    """
    تست auto_send وقتی هیچ سخنرانی آماده‌ای نیست
    """
    service, _, _, mock_db = lecture_service_fixture
    mock_db.auto_return_lecture.return_value = None

    with pytest.raises(Exception) as exc_info:
        await service.auto_send()

    assert "هیچ سخنرانی آماده ارسال نیست" in str(exc_info.value)
