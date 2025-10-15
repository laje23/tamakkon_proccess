import pytest
from unittest.mock import MagicMock, patch
from models.books_model import (
    BooksTableManager,
    create_table,
    save_book,
    edit_book,
    get_unsent_book,
    mark_book_sent,
    get_status,
    check_book_exists,
)

# ---------- Fixture برای Mock کردن اتصال ----------

@pytest.fixture
def mock_db_cursor():
    with patch("models.books_model.get_connection") as mock_conn_func:

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_func.return_value = mock_conn
        yield mock_cursor

# ---------- تست create_table ----------
def test_create_table(mock_db_cursor):
    create_table()
    assert mock_db_cursor.execute.called
    sql = mock_db_cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS books" in sql

# ---------- تست save_book ----------
def test_save_book(mock_db_cursor):
    save_book("کتاب تست", "نویسنده تست")
    sql = mock_db_cursor.execute.call_args[0][0]
    assert "INSERT INTO books" in sql
    params = mock_db_cursor.execute.call_args[0][1]
    assert params[0] == "کتاب تست"
    assert params[1] == "نویسنده تست"

# ---------- تست edit_book ----------
def test_edit_book(mock_db_cursor):
    edit_book(1, "عنوان جدید", "نویسنده جدید")
    sql = mock_db_cursor.execute.call_args[0][0]
    assert "UPDATE books" in sql
    params = mock_db_cursor.execute.call_args[0][1]
    assert params[0] == "عنوان جدید"
    assert params[1] == "نویسنده جدید"
    assert params[-1] == 1

# ---------- تست get_unsent_book ----------
def test_get_unsent_book(mock_db_cursor):
    # Mock کردن fetchone
    mock_db_cursor.fetchone.return_value = (1, "عنوان", "نویسنده", "انتشارات", "چکیده")
    result = get_unsent_book()
    assert result["id"] == 1
    assert result["title"] == "عنوان"

# ---------- تست mark_book_sent ----------
def test_mark_book_sent(mock_db_cursor):
    mark_book_sent(5)
    sql = mock_db_cursor.execute.call_args[0][0]
    assert "UPDATE books SET sent = 1" in sql
    assert mock_db_cursor.execute.call_args[0][1][0] == 5

# ---------- تست get_status ----------
def test_get_status(mock_db_cursor):
    mock_db_cursor.fetchone.side_effect = [(3,), (7,)]
    status = get_status()
    assert status["sent"] == 3
    assert status["unsent"] == 7

# ---------- تست check_book_exists ----------
def test_check_book_exists(mock_db_cursor):
    mock_db_cursor.fetchone.return_value = (True,)
    exists = check_book_exists(1)
    assert exists is True
