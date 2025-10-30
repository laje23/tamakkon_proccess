import pytest
from unittest.mock import AsyncMock, MagicMock
from services.note_service import NoteService, back_menu

@pytest.mark.asyncio
async def test_handle_media_step_photo_video_none():
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    notes_model = MagicMock()
    notes_model.get_state = MagicMock()

    service = NoteService(
        user_temp_data={123: {"note_number": 1, "part_index": 0, "media_type": None, "media_file_id": None}},
        bale_bot=bale_bot,
        eitaa_bot=eitaa_bot
    )
    service.db = notes_model

    # تست عکس، ویدیو و متن 'ندارم'
    test_cases = [
        ("photo", [MagicMock(id="file_photo")], None),
        ("video", None, MagicMock(id="file_video")),
        ("none", None, None)  # متن 'ندارم'
    ]

    for media_type, photo, video in test_cases:
        message = MagicMock()
        message.author.id = 123
        message.chat.id = 456
        message.photo = photo
        message.video = video
        message.text = "ندارم" if media_type == "none" else None
        message.author.set_state = AsyncMock()
        message.author.get_state = MagicMock(return_value="ASK_MEDIA")

        await service.handle_media_step(message)

        if media_type in ["photo", "video"]:
            assert service.user_temp_data[123]["media_type"] == media_type
            assert service.user_temp_data[123]["media_file_id"] is not None
            bale_bot.send_message.assert_awaited()
        else:
            bale_bot.send_message.assert_awaited()


@pytest.mark.asyncio
async def test_handle_text_parts():
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    notes_model = MagicMock()
    notes_model.save_part = AsyncMock()

    service = NoteService(
        user_temp_data={123: {"note_number": 1, "part_index": 0, "media_type": "photo", "media_file_id": "file123"}},
        bale_bot=bale_bot,
        eitaa_bot=eitaa_bot
    )
    service.db = notes_model

    message = MagicMock()
    message.author.id = 123
    message.chat.id = 456
    message.text = "متن بخش 1"
    message.author.set_state = AsyncMock()
    message.author.get_state = MagicMock(return_value="INPUT_TEXT_NOTE")

    await service.handle_text_parts(message)

    notes_model.save_part.assert_called_once_with(1, 0, "متن بخش 1")
    assert service.user_temp_data[123]["part_index"] == 1
    bale_bot.send_message.assert_awaited()


@pytest.mark.asyncio
async def test_confirm_more_text_yes_no():
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    notes_model = MagicMock()
    notes_model.edit_media = AsyncMock()

    service = NoteService(
        user_temp_data={123: {"note_number": 1, "media_type": "photo", "media_file_id": "file123", "part_index": 1}},
        bale_bot=bale_bot,
        eitaa_bot=eitaa_bot
    )
    service.db = notes_model

    # پاسخ بله
    message_yes = MagicMock()
    message_yes.author.id = 123
    message_yes.chat.id = 456
    message_yes.text = "بله"
    message_yes.author.set_state = AsyncMock()

    await service.confirm_more_text(message_yes)
    assert message_yes.author.set_state.called
    bale_bot.send_message.assert_awaited()

    # پاسخ خیر
    service.user_temp_data[123] = {"note_number": 1, "media_type": "photo", "media_file_id": "file123"}
    message_no = MagicMock()
    message_no.author.id = 123
    message_no.chat.id = 456
    message_no.text = "خیر"
    message_no.author.del_state = AsyncMock()
    message_no.author.set_state = AsyncMock()

    await service.confirm_more_text(message_no)
    bale_bot.send_message.assert_awaited()
    assert 123 not in service.user_temp_data


@pytest.mark.asyncio
async def test_auto_send_all_media():
    bale_bot = AsyncMock()
    eitaa_bot = AsyncMock()
    notes_model = MagicMock()
    # متدهای sync
    notes_model.get_unsent_note = MagicMock(return_value=(1, "file123", "photo"))
    notes_model.get_parts = MagicMock(return_value=["part1", "part2"])

    # متدهای async واقعی برای ارسال
    bale_bot.send_photo = AsyncMock()
    bale_bot.send_video = AsyncMock()
    bale_bot.send_message = AsyncMock()
    eitaa_bot.send_file = AsyncMock()
    eitaa_bot.send_message = AsyncMock()

    service = NoteService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    service.db = notes_model

    async def fake_file(file_id, bot):
        class DummyFile:
            async def read(self):
                return b"binary_content"
        return DummyFile()

    service.file_id_to_bynery = fake_file

    # اجرای auto_send برای هر نوع مدیا
    for media_type in ["photo", "video", None]:
        notes_model.get_unsent_note.return_value = (1, "file123" if media_type else None, media_type)
        await service.auto_send()

        # assert sync calls
        notes_model.get_unsent_note.assert_called()
        notes_model.get_parts.assert_called_with(1)

