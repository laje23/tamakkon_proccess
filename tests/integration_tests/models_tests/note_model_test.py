import pytest
from unittest.mock import patch, MagicMock
from models.notes_model import (
    NoteTableManager,
    TextPartManager,
    save_note,
    check_is_exist,
    mark_sent,
    is_note_sent,
    get_status,
    edit_media,
    get_unsent_note,
    save_part,
    get_parts,
    delete_parts,
    update_part,
)


@pytest.fixture
def mock_conn_cursor():
    """اتصال و کرسر جعلی برای شبیه‌سازی پایگاه‌داده"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


# ---------------- NoteTableManager ----------------

def test_create_table_note(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.notes_model.get_connection", return_value=mock_conn):
        db = NoteTableManager()
        db.create_table()
        mock_cursor.execute.assert_called_once()
        assert "CREATE TABLE IF NOT EXISTS notes" in mock_cursor.execute.call_args[0][0]


def test_insert_text_and_exists(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (1,)
    with patch("models.notes_model.get_connection", return_value=mock_conn):
        save_note(123, "file_1", "media_type_1")
        assert mock_cursor.execute.call_count == 1

        exists = check_is_exist(123)
        mock_cursor.execute.assert_called()
        assert exists is not None 


def test_mark_sent_and_is_sent(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (1,)
    with patch("models.notes_model.get_connection", return_value=mock_conn):
        mark_sent(123)
        is_sent_val = is_note_sent(123)
        assert is_sent_val is True
        assert mock_cursor.execute.call_count == 2  # UPDATE + SELECT


def test_get_status_and_edit_media(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.side_effect = [(5,), (3,)]  # sent, unsent
    with patch("models.notes_model.get_connection", return_value=mock_conn):
        result = get_status()
        assert result == {"sent": 5, "unsent": 3}

        edit_media(123, "file_new", "video")
        assert mock_cursor.execute.call_count == 3  # SELECTs + UPDATE


def test_get_unsent_note(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (123, "file_1", "text")
    with patch("models.notes_model.get_connection", return_value=mock_conn):
        result = get_unsent_note()
        assert result == (123, "file_1", "text")
        mock_cursor.execute.assert_called_once()


# ---------------- TextPartManager ----------------

def test_insert_get_delete_part(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchall.return_value = [(0, "part1"), (1, "part2")]
    with patch("models.notes_model.get_connection", return_value=mock_conn):
        save_part(123, 0, "part1")
        save_part(123, 1, "part2")

        parts = get_parts(123)
        assert parts == [(0, "part1"), (1, "part2")]

        delete_parts(123)
        update_part(1, "updated_part")
        # تعداد فراخوانی execute: INSERT x2 + SELECT + DELETE + UPDATE = 5
        assert mock_cursor.execute.call_count == 5
