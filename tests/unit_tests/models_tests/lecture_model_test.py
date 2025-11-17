import pytest
from unittest.mock import MagicMock, patch
from models.lectures_model import (
    LecturesTable,
    create_table,
    save_lecture,
    mark_lecture_sent,
    auto_return_lecture,
    get_status,
)


# ---------- Fixture برای Mock کردن اتصال ----------
@pytest.fixture
def mock_db_cursor():
    with patch("models.lectures_model.get_connection") as mock_conn_func:
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
    assert "CREATE TABLE IF NOT EXISTS lectures" in sql
    conn.commit.assert_called_once()


# ---------- تست save_lecture ----------
def test_save_lecture(mock_db_cursor):
    cursor, conn = mock_db_cursor
    cursor.fetchone.return_value = (0,)
    save_lecture("fileid123", "کپشن تست")

    # بررسی دو اجرای cursor.execute
    assert cursor.execute.call_count == 2

    first_sql = cursor.execute.call_args_list[0][0][0]
    assert "SELECT MIN(sent) FROM lectures" in first_sql

    second_sql = cursor.execute.call_args_list[1][0][0]
    params = cursor.execute.call_args_list[1][0][1]
    assert "INSERT INTO lectures" in second_sql
    assert params == ("fileid123", "کپشن تست", 0)
    conn.commit.assert_called_once()


# ---------- تست mark_lecture_sent ----------
def test_mark_lecture_sent(mock_db_cursor):
    cursor, conn = mock_db_cursor
    mark_lecture_sent(5)
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE lectures SET sent = sent + 1" in sql
    assert params == (5,)
    conn.commit.assert_called_once()


# ---------- تست auto_return_lecture ----------
def test_auto_return_lecture(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (1, "fileid123", "کپشن تست")
    result = auto_return_lecture()
    assert result == (1, "fileid123", "کپشن تست")


def test_auto_return_lecture_none(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = None
    result = auto_return_lecture()
    assert result is None


# ---------- تست get_status ----------
def test_get_status(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.side_effect = [(3,), (7,)]  # unsent, sent
    status = get_status()
    assert status["unsent"] == 3
    assert status["sent"] == 7
