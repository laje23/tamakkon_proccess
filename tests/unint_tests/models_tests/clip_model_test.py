import pytest
from unittest.mock import MagicMock, patch
from models.clips_model import (
    ClipsTable,
    create_table,
    save_clip,
    mark_clip_sent,
    auto_return_file_id,
    get_status,
    check_clip_exists,
    get_last_clip_id,
    edit_clip_caption,
    is_clip_sent,
)


@pytest.fixture
def mock_db_cursor():
    with patch("models.clips_model.get_connection") as mock_conn_func:
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
    assert "CREATE TABLE IF NOT EXISTS clips" in sql
    conn.commit.assert_called_once()


# ---------- تست save_clip ----------
def test_save_clip(mock_db_cursor):
    cursor, conn = mock_db_cursor
    cursor.fetchone.return_value = (1,)
    save_clip("906:12345678", "کپشن تستی")
    assert cursor.execute.call_count == 2

    first_sql = cursor.execute.call_args_list[0][0][0]
    assert "SELECT MIN(sent) FROM clips" in first_sql

    second_sql = cursor.execute.call_args_list[1][0][0]
    assert "INSERT INTO clips" in second_sql

    params = cursor.execute.call_args_list[1][0][1]
    assert params[0] == "906:12345678"
    assert params[1] == "کپشن تستی"
    assert params[2] == 1
    conn.commit.assert_called_once()


# ---------- تست  mark_clip_sent ----------
def test_mark_clip_sent(mock_db_cursor):
    cursor, conn = mock_db_cursor

    mark_clip_sent(5)

    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]

    assert "UPDATE clips SET sent = sent + 1" in sql
    assert params[0] == 5
    conn.commit.assert_called_once()


# ---------- تست auto_return_file_id ----------
def test_auto_return_file_id(mock_db_cursor):
    cursor, _ = mock_db_cursor
    # حالت وقتی fetchone داده داره
    cursor.fetchone.return_value = (1, "file123", "کپشن")
    result = auto_return_file_id()
    assert result == (1, "file123", "کپشن")


def test_auto_return_file_id_none(mock_db_cursor):
    cursor, _ = mock_db_cursor
    # حالت وقتی هیچ داده‌ای نیست
    cursor.fetchone.return_value = None
    result = auto_return_file_id()
    assert result is None


# ---------- تست get_status ----------
def test_get_status(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.side_effect = [(3,), (7,)]
    status = get_status()
    assert status["unsent"] == 3
    assert status["sent"] == 7


# ---------- تست check_clip_exists ----------
def test_check_clip_exists_true(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (1,)
    exists = check_clip_exists(10)
    assert exists is True


def test_check_clip_exists_false(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = None
    exists = check_clip_exists(10)
    assert exists is False


# ---------- تست get_last_clip_id ----------
def test_get_last_clip_id(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (42,)
    last_id = get_last_clip_id()
    assert last_id == 42


def test_get_last_clip_id_none(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (None,)
    last_id = get_last_clip_id()
    assert last_id is None


# ---------- تست edit_clip_caption ----------
def test_edit_clip_caption(mock_db_cursor):
    cursor, conn = mock_db_cursor
    edit_clip_caption(7, "کپشن جدید")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE clips SET caption" in sql
    assert params[0] == "کپشن جدید"
    assert params[1] == 7
    conn.commit.assert_called_once()


# ---------- تست is_clip_sent ----------
def test_is_clip_sent_true(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (3,)
    result = is_clip_sent(8)
    assert result is True


def test_is_clip_sent_false(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (0,)
    result = is_clip_sent(8)
    assert result is False


def test_is_clip_sent_none(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = None
    result = is_clip_sent(8)
    assert result is False
