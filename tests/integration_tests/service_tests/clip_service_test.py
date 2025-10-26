import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from services.clip_service import ClipService
from utils.response import success_response

@pytest.fixture
def mock_bots():
    bale_bot = MagicMock()
    eitaa_bot = MagicMock()
    bale_bot.send_message = AsyncMock()
    bale_bot.send_video = AsyncMock()
    eitaa_bot.send_file = AsyncMock()
    return bale_bot, eitaa_bot

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.auto_return_file_id.return_value = (1, "file123", "My Caption")
    db.save_clip = MagicMock()
    db.edit_clip_caption = MagicMock()
    db.mark_clip_sent = MagicMock()
    return db

@pytest.fixture
def service(mock_bots, mock_db):
    bale_bot, eitaa_bot = mock_bots
    s = ClipService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    s.db = mock_db
    return s, bale_bot, eitaa_bot, mock_db

@pytest.mark.asyncio
@patch("services.clip_service.file_id_to_bynery", new_callable=AsyncMock)
async def test_auto_send(mock_file, service):
    s, bale_bot, eitaa_bot, db = service
    s.bale_channel_id = None
    s.eitaa_channel_id = None
    mock_file.return_value = b"binary_content"

    result = await s.auto_send()

    mock_file.assert_awaited_once_with("file123", bale_bot)
    bale_bot.send_video.assert_awaited_once_with(None, b"binary_content", "My Caption\n\n#کلیپ\n@tamakkon_ir")
    db.mark_clip_sent.assert_called_once_with(1)
    assert "کلیپ با شناسه 1" in result["message"]

@pytest.mark.asyncio
async def test_handle_new_clip_with_video(service):
    s, bale_bot, _, _ = service
    mock_msg = MagicMock()
    mock_msg.author.id = 123
    mock_msg.chat.id = 1
    mock_msg.video = MagicMock()
    mock_msg.video.id = "vid123"
    mock_msg.author.set_state = MagicMock()

    await s.handle_new_clip(mock_msg)

    assert s.user_temp_data[123]["clip_file_id"] == "vid123"
    mock_msg.author.set_state.assert_called_once_with("INPUT_CLIP_CAPTION")
    bale_bot.send_message.assert_awaited_once_with(1, s.MESSAGES["send_caption"])

@pytest.mark.asyncio
async def test_handle_clip_caption(service):
    s, bale_bot, _, db = service
    user_id = 123
    s.user_temp_data[user_id] = {"clip_file_id": "file123"}
    mock_msg = MagicMock()
    mock_msg.author.id = user_id
    mock_msg.chat.id = 1
    mock_msg.text = "My Caption"
    mock_msg.author.del_state = MagicMock()

    await s.handle_clip_caption(mock_msg)

    db.save_clip.assert_called_once_with("file123", "My Caption")
    bale_bot.send_message.assert_awaited_once()
    assert user_id not in s.user_temp_data
    mock_msg.author.del_state.assert_called_once()

@pytest.mark.asyncio
async def test_handle_new_clip_without_video(service):
    s, bale_bot, _, _ = service
    mock_msg = MagicMock()
    mock_msg.author.id = 123
    mock_msg.chat.id = 1
    mock_msg.video = None

    await s.handle_new_clip(mock_msg)
    bale_bot.send_message.assert_awaited_once_with(1, s.MESSAGES["send_clip"])
