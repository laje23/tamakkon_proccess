import pytest
from unittest.mock import MagicMock, patch
from models.audios_model import (
    AudioTableManager,
    create_table,
    insert_audio,
    update_row_by_id,
    get_file_id_and_caption_by_id,
    get_all_audios,
    delete_audio,
)


# ---------- Fixture برای Mock کردن اتصال ----------
@pytest.fixture
def mock_db_cursor():
    with patch("models.audios_model.get_connection") as mock_conn_func:
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
    assert "CREATE TABLE IF NOT EXISTS audio" in sql
    conn.commit.assert_called_once()


# ---------- تست insert_audio ----------
def test_insert_audio(mock_db_cursor):
    cursor, conn = mock_db_cursor
    insert_audio("file1.mp3", "fileid123", "کپشن تست")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "INSERT INTO audio" in sql
    assert params == ("file1.mp3", "fileid123", "کپشن تست")
    conn.commit.assert_called_once()


# ---------- تست update_row_by_id ----------
def test_update_row_by_id(mock_db_cursor):
    cursor, conn = mock_db_cursor
    update_row_by_id(5, "fileid999", "کپشن جدید")
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "UPDATE audio SET file_id" in sql
    assert params == ("fileid999", "کپشن جدید", 5)
    conn.commit.assert_called_once()


# ---------- تست get_file_id_and_caption_by_id ----------
def test_get_file_id_and_caption_by_id(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = ("fileid123", "کپشن تست")
    result = get_file_id_and_caption_by_id(1)
    cursor.execute.assert_called_once()
    assert result == ("fileid123", "کپشن تست")


def test_get_file_id_and_caption_by_id_none(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchone.return_value = None
    result = get_file_id_and_caption_by_id(1)
    assert result is None


# ---------- تست get_all_audios ----------
def test_get_all_audios(mock_db_cursor):
    cursor, _ = mock_db_cursor
    cursor.fetchall.return_value = [
        (1, "file1.mp3", "fileid123", "کپشن تست")
    ]
    result = get_all_audios()
    cursor.execute.assert_called_once()
    assert result == [(1, "file1.mp3", "fileid123", "کپشن تست")]


# ---------- تست delete_audio ----------
def test_delete_audio(mock_db_cursor):
    cursor, conn = mock_db_cursor
    delete_audio(3)
    sql = cursor.execute.call_args[0][0]
    params = cursor.execute.call_args[0][1]
    assert "DELETE FROM audio" in sql
    assert params == (3,)
    conn.commit.assert_called_once()
