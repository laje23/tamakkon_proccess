# tests/services_tests/clip_service_test.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.clip_service import ClipService
import services.clip_service as clip_module  # برای patch کردن تابع file_id_to_bynery

@pytest.fixture
def clip_service_fixture():
    """
    Fixture برای ClipService:
    - یک instance از سرویس
    - mock بات‌های بله و ایتا
    - mock مدل دیتابیس
    """
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    mock_db = MagicMock()

    # ClipService با mocks ساخته می‌شود
    service = ClipService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    service.db = mock_db  # جایگزینی مدل واقعی با mock

    return service, bale_bot, eitaa_bot, mock_db


@pytest.mark.asyncio
async def test_auto_send(clip_service_fixture):
    """
    تست متد auto_send:
    - بررسی اینکه فایل از db گرفته شده و به بات‌ها ارسال شده
    """
    service, _, _, mock_db = clip_service_fixture
    mock_db.auto_return_file_id.return_value = (1, "file_id_1", "کپشن تستی")

    # patch کردن تابع file_id_to_bynery در namespace ClipService
    with patch.object(clip_module, "file_id_to_bynery", new=AsyncMock(return_value=b"fake_bytes")):
        service.send_media = AsyncMock()  # patch متد send_media
        response = await service.auto_send()

        # بررسی اینکه send_media await شده
        service.send_media.assert_awaited_once()

    # بررسی خروجی success_response
    assert "کلیپ با شناسه 1 ارسال شد" in response["message"]
    mock_db.mark_clip_sent.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_handle_new_clip_video(clip_service_fixture):
    """
    تست handle_new_clip وقتی ویدیو ارسال شده
    """
    service, bale_bot, _, _ = clip_service_fixture
    message = MagicMock()
    message.author.id = 123
    message.video.id = "video_id_1"
    message.chat.id = 10

    await service.handle_new_clip(message)

    assert message.author.set_state.call_args[0][0] == "INPUT_CLIP_CAPTION"
    bale_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_new_clip_no_video(clip_service_fixture):
    """
    تست handle_new_clip وقتی ویدیو ارسال نشده
    """
    service, bale_bot, _, _ = clip_service_fixture
    message = MagicMock()
    message.author.id = 123
    message.video = None
    message.chat.id = 10

    await service.handle_new_clip(message)

    bale_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_clip_caption(clip_service_fixture):
    """
    تست handle_clip_caption:
    - بررسی ذخیره کلیپ و پاک شدن state
    """
    service, bale_bot, _, mock_db = clip_service_fixture
    user_id = 123
    service.user_temp_data[user_id] = {"clip_file_id": "file_id_1"}

    message = MagicMock()
    message.author.id = user_id
    message.chat.id = 10
    message.text = "کپشن تستی"

    await service.handle_clip_caption(message)

    mock_db.save_clip.assert_called_once_with("file_id_1", "کپشن تستی")
    bale_bot.send_message.assert_awaited_once()
    assert user_id not in service.user_temp_data
    message.author.del_state.assert_called_once()


@pytest.mark.asyncio
async def test_handle_edit_caption(clip_service_fixture):
    """
    تست handle_edit_caption:
    - بررسی ویرایش کپشن و ارسال پیام موفقیت
    """
    service, bale_bot, _, mock_db = clip_service_fixture
    user_id = 123
    service.user_temp_data[user_id] = {"edit_id": 5}

    message = MagicMock()
    message.author.id = user_id
    message.chat.id = 10
    message.text = "کپشن جدید"

    await service.handle_edit_caption(message)

    mock_db.edit_clip_caption.assert_called_once_with(5, "کپشن جدید")
    bale_bot.send_message.assert_awaited_once()
    assert user_id not in service.user_temp_data
    message.author.del_state.assert_called_once()
