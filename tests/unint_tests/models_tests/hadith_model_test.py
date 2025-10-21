import pytest
from unittest.mock import MagicMock, patch
from models.hadith_model import (
    HadithTableManager,
    create_table,
    save_id_and_content,
    edit_content,
    return_auto_content,
    mark_sent,
    get_status,
)


# ---------- Fixture برای Mock کردن اتصال ----------
@pytest.fixture
def mock_db_cursor():
    with patch("models.hadith_model.get_connection") as mock_conn_func:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_func.return_value = mock_conn
        yield mock_cursor, mock_conn


# ---------- تست create_table ----------
def test_create_table(mock_db_cursor):
    cursor, conn = mock_db_cursor
    create_table()
    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS hadith" in sql
    conn.commit.assert_called_once()


# ---------- تست save_id_and_content ----------
def test_save_id_and_content(mock_db_cursor):
    cursor, conn = mock_db_cursor
    cursor.fetchone.return_value = (0,)  # کمترین sent موجود
    save_id_and_content(123, "متن حدیث")
    assert cursor.execute.call_count == 2

    first_sql = cursor.execute.call_args_list[0][0][0]
    assert "SELECT MIN(sent) FROM hadith" in first_sql

    second_sql = cursor.execute.call_args_list[1][0][0]
    params = cursor.execute.call_args_list[1][0][1]
    assert "INSERT INTO hadith" in second_sql
    assert params == (123, "متن حدیث", 0)
    conn.commit.assert_called_once()


# ---------- تست edit_content ----------
def test_edit_content(mock_db_cursor):
    cursor, conn = mock_db_cursor
    edit_content(123, "محتوای جدید")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE hadith SET content" in sql
    assert params == ("محتوای جدید", 123)
    conn.commit.assert_called_once()


# ---------- تست return_auto_content ----------
def test_return_auto_content(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = ("متن حدیث تست", 5)
    result = return_auto_content()
    assert result == ("متن حدیث تست", 5)


def test_return_auto_content_none(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = None
    result = return_auto_content()
    assert result is None


# ---------- تست mark_sent ----------
def test_mark_sent(mock_db_cursor):
    cursor, conn = mock_db_cursor
    mark_sent(5, "متن حدیث")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE hadith SET sent = 1" in sql
    assert params == (5, "متن حدیث")
    conn.commit.assert_called_once()


# ---------- تست get_status ----------
def test_get_status(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.side_effect = [(7,), (3,)]  # unsent, sent
    status = get_status()
    assert status["unsent"] == 7
    assert status["sent"] == 3
