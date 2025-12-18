# tests/unit_tests/services_tests/qaa_service_test.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.qaa_service import QAAService

# ---------------- fixtures ---------------- #

@pytest.fixture
def mock_author():
    author = MagicMock()
    author.id = 1234
    author.set_state = MagicMock()
    author.del_state = MagicMock()
    return author

@pytest.fixture
def mock_bot():
    return AsyncMock()

@pytest.fixture
def mock_collection_model():
    model = MagicMock()
    model.collection_exists.return_value = False
    model.add_collection.return_value = 42
    return model

@pytest.fixture
def mock_question_model():
    model = MagicMock()
    model.get_question_count.return_value = 1
    model.get_question.return_value = (1, 42, 1, "سوال تست", "a", "b", "c", "correct")
    return model

@pytest.fixture
def mock_user_model():
    return MagicMock()

@pytest.fixture
def qaa_service(mock_bot, mock_collection_model, mock_question_model, mock_user_model):
    return QAAService(
        bale_bot=mock_bot,
        qaa_collection=mock_collection_model,
        qaa_question=mock_question_model,
        user_model=mock_user_model
    )

# ---------------- save_qaa_title ---------------- #

@pytest.mark.asyncio
async def test_save_qaa_title_new_collection(qaa_service, mock_author, mock_bot, mock_collection_model):
    # وقتی collection وجود ندارد
    mock_collection_model.collection_exists.return_value = False

    # patch کردن back_to_message_menu
    with patch("services.qaa_service.back_to_message_menu", return_value="keyboard_mock"):
        await qaa_service.save_qaa_title(mock_author, "جدید")

    mock_collection_model.add_collection.assert_called_once_with("جدید")
    mock_bot.send_message.assert_awaited_once_with(
        mock_author.id,
        "با موفقیت ذخیره شد",
        "keyboard_mock"
    )


@pytest.mark.asyncio
async def test_save_qaa_title_existing_collection(qaa_service, mock_author, mock_bot, mock_collection_model):
    # وقتی collection از قبل وجود دارد
    mock_collection_model.collection_exists.return_value = True

    with patch("services.qaa_service.back_to_message_menu", return_value="keyboard_mock"):
        await qaa_service.save_qaa_title(mock_author, "وجود دارد")

    mock_bot.send_message.assert_awaited_once_with(
        mock_author.id,
        "شما آن را دارید\nلطفا عنوانی جدید وارد کنید",
        "keyboard_mock"
    )

# ---------------- save_qaa_state_1 ---------------- #

@pytest.mark.asyncio
async def test_save_qaa_state_1_sets_temp_data(qaa_service, mock_author, mock_bot):
    await qaa_service.save_qaa_state_1(mock_author, 42)

    assert qaa_service.user_temp_data[mock_author.id]["collection_id"] == 42
    mock_bot.send_message.assert_awaited_once_with(mock_author.id, "متن پرسش رو وارد کن")
    mock_author.set_state.assert_called_once_with("ENTER_QAA_TEXT")

# ---------------- do_qaa_conf ---------------- #

@pytest.mark.asyncio
async def test_do_qaa_conf_sets_buttons_and_state(qaa_service, mock_author, mock_bot):
    collection_id = 1
    message_id = 99

    await qaa_service.do_qaa_conf(mock_author, message_id, collection_id)

    assert mock_author.set_state.called
    mock_bot.edit_message_text.assert_awaited_once()
    args = mock_bot.edit_message_text.call_args[0]
    assert args[0] == mock_author.id
    assert args[1] == message_id
    assert "سوال تست" in args[2]

# ---------------- handel_qaa_answers ---------------- #

@pytest.mark.asyncio
async def test_handel_qaa_answers_completes(qaa_service, mock_author, mock_bot, mock_user_model):
    # آماده‌سازی user_temp_data برای یک سوال
    qaa_service.user_temp_data[mock_author.id] = {
        "question_index": 1,
        "collection_id": 1,
        "max_index": 1,
        "answer:1": "good"
    }

    message_id = 123
    await qaa_service.handel_qaa_answers(mock_author, message_id, "good")

    # بررسی فراخوانی add_result و پاک شدن temp_data
    mock_user_model.add_result.assert_called_once_with(mock_author.id, 1, 1)
    assert mock_author.del_state.called
    assert mock_author.id not in qaa_service.user_temp_data
    mock_bot.edit_message_text.assert_awaited_once()
