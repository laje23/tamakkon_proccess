# tests/services_tests/note_service_test.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.note_service import NoteService
import tracemalloc
tracemalloc.start()


@pytest.fixture
def note_service_fixture():
    """
    Fixture برای NoteService:
    - instance از سرویس
    - mock بات‌ها
    - mock مدل دیتابیس
    """
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    mock_db = MagicMock()

    service = NoteService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    service.bale_channel_id = 1234567
    service.eitaa_channel_id = 7654321
    service.db = mock_db  # جایگزینی مدل واقعی با mock
    return service, bale_bot, eitaa_bot, mock_db


@pytest.mark.asyncio
async def test_auto_send_test_photo(note_service_fixture):
    service, bale_bot, eitaa_bot, mock_db = note_service_fixture

    # 🟢 مرحله ۱: تنظیم بازگشت دیتابیس برای ورود به مسیر photo
    mock_db.get_unsent_note.return_value = (1, "fake_file_id", "photo")
    mock_db.get_parts.return_value = ["متن تستی"]

    # 🟢 مرحله ۲: شبیه‌سازی تابع prepare_processed_messages و success_response
    # توجه کن که باید patch بشن تا در محدوده‌ی فایل note_service باشند
    with patch("services.note_service.prepare_processed_messages") as mock_prepare, \
        patch("services.note_service.file_id_to_bynery") as mock_file_id_to_bynery, \
        patch("services.note_service.success_response") as mock_success:

        # تنظیم mockها:
        mock_prepare.return_value = ["message"]
        mock_success.return_value = {"message": "یادداشت ارسال شد"}

        # این تابع async هست، پس باید یک awaitable برگردونه
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake binary"
        mock_file_id_to_bynery.return_value = mock_file  # نیازی به AsyncMock نیست چون در await resolve میشه

        # شبیه‌سازی ارسال پیام‌ها
        bale_bot.send_photo = AsyncMock()
        eitaa_bot.send_file = AsyncMock()

        # 🟢 اجرای تابع داخل context patch
        respon = await service.auto_send()

    # 🟢 مرحله ۳: بررسی فراخوانی‌ها
    bale_bot.send_photo.assert_awaited_once()
    eitaa_bot.send_file.assert_awaited_once()
    mock_db.mark_sent.assert_called_once_with(1)

    assert "یادداشت ارسال شد" in respon["message"]


@pytest.mark.asyncio
async def test_auto_send_no_note(note_service_fixture):
    """
    تست auto_send وقتی هیچ یادداشتی موجود نیست
    """
    service, _, _, mock_db = note_service_fixture
    mock_db.get_unsent_note.return_value = None

    response = await service.auto_send()
    assert response["success"] == False
    assert "هیچ یادداشتی برای ارسال موجود نیست" in response["error_message"]


@pytest.mark.asyncio
async def test_first_step_save_new_note(note_service_fixture):
    """
    تست first_step_save وقتی یادداشت جدید ایجاد می‌کنیم
    """
    service, bale_bot, _, mock_db = note_service_fixture
    mock_db.check_is_exist.return_value = False
    service.user_temp_data = {"note_number":123456789, "media_type": None, "media_file_id": None, "part_index": 0,}

    message = MagicMock()
    message.text = "1"
    message.chat.id = 10
    message.author.id = 123
    message.author.set_state = MagicMock()

    await service.first_step_save(message)

    mock_db.save_note.assert_called_once_with(1, "", "")
    assert service.user_temp_data[123]["note_number"] == 1
    message.author.set_state.assert_called_once_with("ASK_MEDIA")
    bale_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_first_step_save_existing_note(note_service_fixture):
    """
    تست first_step_save وقتی یادداشت از قبل موجود است
    """
    service, bale_bot, _, mock_db = note_service_fixture
    mock_db.check_is_exist.return_value = True
    service.user_temp_data = {"note_number":123456789, "media_type": None, "media_file_id": None, "part_index": 0,}

    message = MagicMock()
    message.text = "1"
    message.chat.id = 10
    message.author.id = 123
    message.author.set_state = MagicMock()

    await service.first_step_save(message)

    mock_db.save_note.assert_not_called()
    bale_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_handle_text_parts(note_service_fixture):
    """
    تست handle_text_parts ذخیره بخش متن
    """
    service, bale_bot, _, mock_db = note_service_fixture
    service.user_temp_data = {"note_number":123456789, "media_type": None, "media_file_id": None, "part_index": 0,}
    service.user_temp_data[123] = {"note_number": 1, "part_index": 0}

    message = MagicMock()
    message.author.id = 123
    message.author.get_state.return_value = "INPUT_TEXT_NOTE"
    message.chat.id = 10
    message.text = "متن بخش اول"

    await service.handle_text_parts(message)

    mock_db.save_part.assert_called_once_with(1, 0, "متن بخش اول")
    assert service.user_temp_data[123]["part_index"] == 1
    bale_bot.send_message.assert_awaited_once()


@pytest.mark.asyncio
async def test_confirm_more_text_yes_no(note_service_fixture):
    """
    تست confirm_more_text پاسخ بله و خیر
    """
    service, bale_bot, _, mock_db = note_service_fixture
    service.user_temp_data = {"note_number":123456789, "media_type": None, "media_file_id": None, "part_index": 0,}
    user_id = 123
    service.user_temp_data[user_id] = {"note_number": 1}

    # پاسخ بله
    message_yes = MagicMock()
    message_yes.author.id = user_id
    message_yes.text = "بله"
    message_yes.chat.id = 10
    message_yes.author.set_state = MagicMock()

    await service.confirm_more_text(message_yes)
    message_yes.author.set_state.assert_called_once_with("INPUT_TEXT_NOTE")
    bale_bot.send_message.assert_awaited_once()

    # پاسخ خیر
    service.user_temp_data[user_id] = {"note_number": 1}
    message_no = MagicMock()
    message_no.author.id = user_id
    message_no.text = "خیر"
    message_no.chat.id = 10
    message_no.author.del_state = MagicMock()

    await service.confirm_more_text(message_no)
    mock_db.edit_media.assert_called_once()
    message_no.author.del_state.assert_called_once()
    bale_bot.send_message.assert_awaited()  # پیام ذخیره شده
