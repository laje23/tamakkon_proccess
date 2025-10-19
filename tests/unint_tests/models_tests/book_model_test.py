import pytest
from unittest.mock import MagicMock, patch
from models.books_model import (
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
        yield mock_cursor, mock_conn


# ---------- تست create_table ----------
def test_create_table(mock_db_cursor):
    cursor, conn = mock_db_cursor
    create_table()
    assert cursor.execute.called
    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS books" in sql
    conn.commit.assert_called_once()


# ---------- تست save_book ----------
def test_save_book(mock_db_cursor):
    cursor, conn = mock_db_cursor
    save_book("کتاب تست", "نویسنده تست")
    sql = cursor.execute.call_args[0][0]
    assert "INSERT INTO books" in sql
    params = cursor.execute.call_args[0][1]
    assert params[0] == "کتاب تست"
    assert params[1] == "نویسنده تست"
    conn.commit.assert_called_once()


# ---------- تست edit_book ----------
def test_edit_book(mock_db_cursor):
    cursor, conn = mock_db_cursor
    edit_book(1, "عنوان جدید", "نویسنده جدید")
    sql = cursor.execute.call_args[0][0]
    assert "UPDATE books" in sql
    params = cursor.execute.call_args[0][1]
    assert params[0] == "عنوان جدید"
    assert params[1] == "نویسنده جدید"
    assert params[-1] == 1
    conn.commit.assert_called_once()


# ---------- تست get_unsent_book ----------
def test_get_unsent_book(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (1, "عنوان", "نویسنده", "انتشارات", "چکیده")
    result = get_unsent_book()
    assert result["id"] == 1
    assert result["title"] == "عنوان"


def test_get_unsent_book_none(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = None
    result = get_unsent_book()
    assert result is None


# ---------- تست mark_book_sent ----------
def test_mark_book_sent(mock_db_cursor):
    cursor, conn = mock_db_cursor
    mark_book_sent(5)
    sql = cursor.execute.call_args[0][0]
    assert "UPDATE books SET sent = 1" in sql
    assert cursor.execute.call_args[0][1][0] == 5
    conn.commit.assert_called_once()


# ---------- تست get_status ----------
def test_get_status(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.side_effect = [(3,), (7,)]
    status = get_status()
    assert status["sent"] == 3
    assert status["unsent"] == 7


# ---------- تست check_book_exists ----------
def test_check_book_exists(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (True,)
    exists = check_book_exists(1)
    assert exists is True
