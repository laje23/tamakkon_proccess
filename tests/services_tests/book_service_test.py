# tests/services_tests/test_book_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from services.book_service import BookService


@pytest.fixture
def user_data():
    """دیکشنری موقت برای ذخیره داده‌های کاربر"""
    return {}

@pytest.fixture
def mock_bots():
    """ساخت AsyncMock برای بات‌های بله و ایتا"""
    return AsyncMock(), AsyncMock()

@pytest.fixture
def book_service(user_data, mock_bots):
    """ساخت نمونه BookService"""
    bale_bot, eitaa_bot = mock_bots
    service = BookService(user_temp_data=user_data, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
    # جایگزینی db مدل با mock
    service.db = MagicMock()
    return service

@pytest.mark.asyncio
async def test_input_book_title(book_service, user_data):
    """تست دریافت عنوان کتاب"""
    message = MagicMock()
    message.text = "کتاب تستی"
    message.author.id = 1
    message.chat.id = 10
    message.author.set_state = MagicMock()

    await book_service.input_book_title(message)

    # بررسی ذخیره عنوان در user_temp_data
    assert user_data[1]["title"] == "کتاب تستی"
    # بررسی تغییر وضعیت
    message.author.set_state.assert_called_with("INPUT_BOOK_AUTHOR")
    # بررسی ارسال پیام
    book_service.bale_bot.send_message.assert_awaited_once()

@pytest.mark.asyncio
async def test_input_book_author(book_service, user_data):
    """تست دریافت نام نویسنده"""
    user_data[1] = {"title": "کتاب تستی"}
    message = MagicMock()
    message.text = "نویسنده تستی"
    message.author.id = 1
    message.chat.id = 10
    message.author.set_state = MagicMock()

    await book_service.input_book_author(message)

    assert user_data[1]["author"] == "نویسنده تستی"
    message.author.set_state.assert_called_with("INPUT_BOOK_PUBLISHER")
    book_service.bale_bot.send_message.assert_awaited_once()

@pytest.mark.asyncio
async def test_input_book_publisher(book_service, user_data):
    """تست دریافت نام ناشر"""
    user_data[1] = {"title": "کتاب تستی", "author": "نویسنده تستی"}
    message = MagicMock()
    message.text = "ناشر تستی"
    message.author.id = 1
    message.chat.id = 10
    message.author.set_state = MagicMock()

    await book_service.input_book_publisher(message)

    assert user_data[1]["publisher"] == "ناشر تستی"
    message.author.set_state.assert_called_with("INPUT_BOOK_EXCERPT")
    book_service.bale_bot.send_message.assert_awaited_once()

@pytest.mark.asyncio
async def test_input_book_excerpt(book_service, user_data):
    """تست دریافت گزیده کتاب و ذخیره در دیتابیس"""
    user_data[1] = {"title": "کتاب تستی", "author": "نویسنده تستی", "publisher": "ناشر تستی"}
    message = MagicMock()
    message.text = "گزیده تستی"
    message.author.id = 1
    message.chat.id = 10
    message.author.del_state = MagicMock()

    await book_service.input_book_excerpt(message)

    # بررسی اینکه متد save_book در db صدا زده شده
    book_service.db.save_book.assert_called_once_with(
        title="کتاب تستی",
        author="نویسنده تستی",
        publisher="ناشر تستی",
        excerpt="گزیده تستی",
    )
    # بررسی پاک شدن داده کاربر
    assert 1 not in user_data
    # بررسی حذف وضعیت کاربر
    message.author.del_state.assert_called_once()
    book_service.bale_bot.send_message.assert_awaited_once()
