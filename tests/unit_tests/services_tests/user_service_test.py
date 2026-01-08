import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.user_service import UserService

# ---------------- fixtures ---------------- #


@pytest.fixture
def mock_author():
    author = MagicMock()
    author.id = 1234
    author.set_state = MagicMock()
    return author


@pytest.fixture
def mock_user_model():
    return MagicMock()


@pytest.fixture
def mock_bot():
    return AsyncMock()


@pytest.fixture
def user_service(mock_user_model, mock_bot):
    return UserService(user_model=mock_user_model, bale_bot=mock_bot)


# -------- handel_login_button -------- #
@pytest.mark.asyncio
async def test_handel_login_button(user_service, mock_author, mock_bot):
    message_id = 42
    # مسیر patch اصلاح شد به مسیر import شده داخل UserService
    with patch("services.user_service.back_to_main_menu", return_value="keyboard_mock"):
        await user_service.handel_login_button(mock_author, message_id)

    # بررسی فراخوانی بات و تغییر state
    mock_bot.edit_message_text.assert_awaited_once_with(
        mock_author.id,
        message_id,
        "خوش آمدید لطفا نام خود را وارد کنید",
        "keyboard_mock",
    )
    mock_author.set_state.assert_called_once_with("LOGIN")


# -------- insert_user -------- #
@pytest.mark.asyncio
async def test_insert_user(user_service, mock_author, mock_user_model, mock_bot):
    name = "Ali"

    # مسیر patch اصلاح شد به مسیر import شده داخل UserService
    with patch("services.user_service.main_menu", return_value="main_menu_mock"):
        await user_service.insert_user(mock_author, name)

    # بررسی فراخوانی add_user و ارسال پیام
    mock_user_model.add_user.assert_called_once_with(mock_author.id, name)
    mock_bot.send_message.assert_awaited_once_with(
        mock_author.id, " تبریک میگم شما وارد شدید.", "main_menu_mock"
    )
