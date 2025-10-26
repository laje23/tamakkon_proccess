import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.lecture_service import LectureService
from utils.response import success_response

@pytest.fixture
def mock_bots():
    bale_bot = MagicMock()
    eitaa_bot = MagicMock()
    bale_bot.send_audio = AsyncMock()
    bale_bot.send_message = AsyncMock()
    bale_bot.send_photo = AsyncMock()
    bale_bot.send_video = AsyncMock()

    eitaa_bot.send_file = AsyncMock()
    eitaa_bot.send_message = AsyncMock()
    return bale_bot, eitaa_bot

@pytest.mark.asyncio
@patch("services.lecture_service.file_id_to_bynery", new_callable=AsyncMock)
async def test_auto_send_success(mock_file, mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = LectureService(bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    # ماک دیتابیس
    lecture_id = 101
    file_id = "file123"
    caption = "lecture caption"
    service.db.auto_return_lecture = MagicMock(return_value=(lecture_id, file_id, caption))
    service.db.mark_lecture_sent = MagicMock()

    # ماک فایل باینری
    bin_mock = AsyncMock()
    mock_file.return_value = bin_mock

    # ماک send_media
    service.send_media = AsyncMock()

    result = await service.auto_send()

    service.db.auto_return_lecture.assert_called_once()
    mock_file.assert_awaited_once_with(file_id, bale_bot)
    service.send_media.assert_awaited_once_with("audio", bin_mock, caption + "\n\n#سخنرانی\n@tamakkon_ir")
    service.db.mark_lecture_sent.assert_called_once_with(lecture_id)
    assert result["message"] == f"سخنرانی با شناسه {lecture_id} ارسال شد"


@pytest.mark.asyncio
async def test_auto_send_no_lecture(mock_bots):
    bale_bot, eitaa_bot = mock_bots
    service = LectureService(bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    # دیتابیس هیچ سخنرانی ندارد
    service.db.auto_return_lecture = MagicMock(return_value=None)

    result = await service.auto_send()

    service.db.auto_return_lecture.assert_called_once()
    assert result["success"] is False
    assert "هیچ سخنرانی آماده ارسال نیست" in result["error_message"]

