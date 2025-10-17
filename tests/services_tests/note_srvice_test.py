# tests/services_tests/note_service_test.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.note_service import NoteService

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
async def test_auto_send_success(note_service_fixture):
    service, bale_bot, eitaa_bot, mock_db = note_service_fixture

    # داده‌های دیتابیس
    mock_db.get_unsent_note.return_value = (7, "file_id_1", "photo")
    mock_db.get_parts.return_value = ["بخش اول متن", "بخش دوم متن"]

    # فایل و پیام دلخواه
    mock_file = b"fake_bytes"
    mock_message = "پیام تستی"

    # patch کردن تابع تولید پیام و تبدیل file_id به فایل
    with patch("services.note_service.prepare_processed_messages", return_value=[mock_message]), \
        patch("services.note_service.file_id_to_bynery", new=AsyncMock(return_value=mock_file)):

        # mock کردن متدهای بات
        service.bale_bot.send_photo = AsyncMock()
        service.eitaa_bot.send_file = AsyncMock()
        service.bale_bot.send_message = AsyncMock()
        service.eitaa_bot.send_message = AsyncMock()

        response = await service.auto_send()

        # چک کردن فراخوانی‌ها
        service.bale_bot.send_photo.assert_awaited_once_with(service.bale_channel_id, mock_file, mock_message)
        service.eitaa_bot.send_file.assert_awaited_once_with(service.eitaa_channel_id, mock_file, mock_message)
        service.bale_bot.send_message.assert_awaited()
        service.eitaa_bot.send_message.assert_awaited()

    mock_db.mark_sent.assert_called_once_with(7)
    assert response["success"] is True
    assert "یادداشت ارسال شد" in response["message"]



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
