import pytest
from unittest.mock import MagicMock, AsyncMock
from services.book_service import BookService
from models import books_model
from utils.response import success_response

@pytest.fixture
def mock_bots():
    bale_bot = MagicMock()
    eitaa_bot = MagicMock()
    bale_bot.send_message = AsyncMock()
    eitaa_bot.send_message = AsyncMock()
    return bale_bot, eitaa_bot

@pytest.fixture
def mock_db():
    db = MagicMock()
    db.get_unsent_book.return_value = {
        "id": 1,
        "title": "Test Book",
        "author": "Test Author",
        "publisher": "Test Publisher",
        "excerpt": "Test Excerpt",
    }
    db.check_book_exists.return_value = True
    db.save_book = MagicMock()
    db.edit_book = MagicMock()
    db.mark_book_sent = MagicMock()
    return db

@pytest.fixture
def service(mock_bots, mock_db):
    bale_bot, eitaa_bot = mock_bots
    s = BookService(user_temp_data={}, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    s.db = mock_db
    return s, bale_bot, eitaa_bot

@pytest.mark.asyncio
async def test_auto_send(service):
    s, bale_bot, eitaa_bot = service
    result = await s.auto_send()
    bale_bot.send_message.assert_awaited_once()
    eitaa_bot.send_message.assert_awaited_once()
    s.db.mark_book_sent.assert_called_once_with(1)
    assert "Test Book" in result["message"]

@pytest.mark.asyncio
async def test_input_book_flow(service):
    s, bale_bot, _ = service
    user_id = 123
    mock_msg = MagicMock()
    mock_msg.author.id = user_id
    mock_msg.chat.id = 1
    mock_msg.text = "My Title"
    mock_msg.author.set_state = MagicMock()

    await s.input_book_title(mock_msg)
    assert s.user_temp_data[user_id]["title"] == "My Title"
    mock_msg.author.set_state.assert_called_with("INPUT_BOOK_AUTHOR")

    # author
    mock_msg.text = "My Author"
    await s.input_book_author(mock_msg)
    assert s.user_temp_data[user_id]["author"] == "My Author"

    # publisher
    mock_msg.text = "ندارم"
    await s.input_book_publisher(mock_msg)
    assert s.user_temp_data[user_id]["publisher"] is None

    # excerpt
    mock_msg.text = "Excerpt text"
    mock_msg.author.del_state = MagicMock()
    await s.input_book_excerpt(mock_msg)
    assert user_id not in s.user_temp_data
    mock_msg.author.del_state.assert_called_once()
    s.db.save_book.assert_called_once_with(
        title="My Title",
        author="My Author",
        publisher=None,
        excerpt="Excerpt text",
    )

@pytest.mark.asyncio
async def test_input_book_id_for_edit_invalid(service):
    s, bale_bot, _ = service
    mock_msg = MagicMock()
    mock_msg.author.id = 123
    mock_msg.chat.id = 1
    mock_msg.text = "not_a_number"
    mock_msg.author.del_state = MagicMock()

    await s.input_book_id_for_edit(mock_msg)
    bale_bot.send_message.assert_awaited_once()
