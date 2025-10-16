import pytest
from unittest.mock import AsyncMock, patch
from services.general_service import GeneralService

# ⚡ این مارک لازم است تا pytest async functions را بشناسد
pytestmark = pytest.mark.asyncio


# Fixture اصلی سرویس با Mock بات‌ها و Mock تابع async file_id_to_bynery
@pytest.fixture
def general_service_fixture():
    # ساخت AsyncMock برای بات‌ها
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    user_temp_data = {}

    # نمونه سرویس
    service = GeneralService(user_temp_data, bale_bot, eitaa_bot)

    # Mock تابع async file_id_to_bynery
    with patch("services.general_service.file_id_to_bynery", new_callable=AsyncMock) as mock_file_id_to_bynery:
        # Mock object که read async دارد
        mock_bin_file = AsyncMock()
        mock_bin_file.read.return_value = b"fake audio data"
        mock_file_id_to_bynery.return_value = mock_bin_file

        # Mock تابع success_response
        with patch("services.general_service.success_response") as mock_success:
            mock_success.side_effect = lambda msg: {"status": "success", "msg": msg}
            yield service, bale_bot, eitaa_bot, mock_file_id_to_bynery


# ===========================
# تست send_audio_file
# ===========================
@pytest.mark.asyncio
async def test_send_audio_file(general_service_fixture):
    service, bale_bot, eitaa_bot, mock_file_id_to_bynery = general_service_fixture

    response = await service.send_audio_file("fake_file_id", "کپشن تستی")

    # assert صدا زده شدن async بات‌ها
    bale_bot.send_audio.assert_awaited_once()
    eitaa_bot.send_file.assert_awaited_once()

    # assert خروجی success_response
    assert response["status"] == "success"
    assert "فایل صوتی ارسال شد" in response["msg"]


# ===========================
# تست send_text_message
# ===========================
@pytest.mark.asyncio
async def test_send_text_message(general_service_fixture):
    service, bale_bot, eitaa_bot, _ = general_service_fixture

    response = await service.send_text_message("پیام تستی")

    bale_bot.send_message.assert_awaited_once()
    eitaa_bot.send_message.assert_awaited_once()

    assert response["status"] == "success"
    assert "پیام متنی ارسال شد" in response["msg"]


# ===========================
# تست send_photo_with_text
# ===========================
@pytest.mark.asyncio
async def test_send_photo_with_text(general_service_fixture):
    service, bale_bot, eitaa_bot, _ = general_service_fixture

    response = await service.send_photo_with_text("fake_photo_path", "متن تست")

    bale_bot.send_photo.assert_awaited_once()
    eitaa_bot.send_file.assert_awaited_once()

    assert response["status"] == "success"
    assert "پیام تصویری ارسال شد" in response["msg"]
