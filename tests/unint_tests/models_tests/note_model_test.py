import pytest
from unittest.mock import MagicMock, patch
from models.notes_model import (
    create_table_parts,
    save_part,
    get_parts,
    delete_parts,
    update_part,
    create_table,
    save_note,
    check_is_exist,
    mark_sent,
    is_note_sent,
    get_status,
    edit_media,
    get_unsent_note,
)


# ---------- Fixture برای Mock کردن connection ----------
@pytest.fixture
def mock_db_cursor():
    with patch("models.notes_model.get_connection") as mock_conn_func:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_func.return_value = mock_conn
        yield mock_cursor, mock_conn


# ---------- تست توابع TextPartManager ----------
def test_create_table_parts(mock_db_cursor):
    cursor, conn = mock_db_cursor
    create_table_parts()
    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS note_patrs" in sql
    conn.commit.assert_called_once()


def test_save_part(mock_db_cursor):
    cursor, conn = mock_db_cursor
    save_part(1, 0, "content test")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "INSERT INTO note_patrs" in sql
    assert params == (1, 0, "content test")
    conn.commit.assert_called_once()


def test_get_parts(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchall.return_value = [(0, "content test")]
    result = get_parts(1)
    assert result == [(0, "content test")]
    cursor.execute.assert_called_once()


def test_delete_parts(mock_db_cursor):
    cursor, conn = mock_db_cursor
    delete_parts(1)
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "DELETE FROM note_patrs" in sql
    assert params == (1,)
    conn.commit.assert_called_once()


def test_update_part(mock_db_cursor):
    cursor, conn = mock_db_cursor
    update_part(5, "new content")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE note_patrs SET content" in sql
    assert params == ("new content", 5)
    conn.commit.assert_called_once()


# ---------- تست توابع NoteTableManager ----------
def test_create_table(mock_db_cursor):
    cursor, conn = mock_db_cursor
    create_table()
    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS notes" in sql
    conn.commit.assert_called_once()


def test_save_note(mock_db_cursor):
    cursor, conn = mock_db_cursor
    save_note(1, "fileid123", "media")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "INSERT INTO notes" in sql
    assert params == (1, "fileid123", "media")
    conn.commit.assert_called_once()


def test_check_is_exist(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (True,)
    result = check_is_exist(1)
    assert result is True
    cursor.execute.assert_called_once()


def test_mark_sent(mock_db_cursor):
    cursor, conn = mock_db_cursor
    mark_sent(1)
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE notes SET sent = 1" in sql
    assert params == (1,)
    conn.commit.assert_called_once()


def test_is_note_sent(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (1,)
    result = is_note_sent(1)
    assert result is True

    cursor.fetchone.return_value = (0,)
    result = is_note_sent(2)
    assert result is False


def test_get_status(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.side_effect = [(5,), (3,)]
    status = get_status()
    assert status["sent"] == 5
    assert status["unsent"] == 3


def test_edit_media(mock_db_cursor):
    cursor, conn = mock_db_cursor
    edit_media(1, "fileid999", "new media")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE notes" in sql
    assert params == ("fileid999", "new media", 1)
    conn.commit.assert_called_once()


def test_get_unsent_note(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = (1, "fileid123", "media")
    result = get_unsent_note()
    assert result == (1, "fileid123", "media")
