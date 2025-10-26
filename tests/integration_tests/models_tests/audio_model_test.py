import pytest
from unittest.mock import patch, MagicMock
from models.audios_model import (
    AudioTableManager,
    insert_audio,
    get_all_audios,
    get_file_id_and_caption_by_id,
    update_row_by_id,
    delete_audio,
)

@pytest.fixture
def mock_db_connection():
    """اتصال جعلی دیتابیس با cursor شبیه‌سازی شده"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


def test_insert_audio(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    # mock کردن get_connection تا اتصال جعلی برگردونه
    with patch("models.audios_model.get_connection", return_value=mock_conn):
        insert_audio("test.mp3", "f123", "caption test")

        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO audio (filename, file_id, caption) VALUES (%s, %s, %s)",
            ("test.mp3", "f123", "caption test"),
        )
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()


def test_get_all_audios(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchall.return_value = [
        (1, "a.mp3", "fid1", "cap1"),
        (2, "b.mp3", "fid2", "cap2"),
    ]

    with patch("models.audios_model.get_connection", return_value=mock_conn):
        result = get_all_audios()

        mock_cursor.execute.assert_called_once_with(
            "SELECT id, filename, file_id, caption FROM audio"
        )
        assert result == [
            (1, "a.mp3", "fid1", "cap1"),
            (2, "b.mp3", "fid2", "cap2"),
        ]
        mock_conn.close.assert_called_once()


def test_get_file_id_and_caption_by_id(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = ("file123", "caption123")

    with patch("models.audios_model.get_connection", return_value=mock_conn):
        result = get_file_id_and_caption_by_id(1)

        mock_cursor.execute.assert_called_once_with(
            "SELECT file_id, caption FROM audio WHERE id = %s LIMIT 1", (1,)
        )
        assert result == ("file123", "caption123")


def test_update_row_by_id(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    with patch("models.audios_model.get_connection", return_value=mock_conn):
        update_row_by_id(1, "new_fid", "new_cap")

        mock_cursor.execute.assert_called_once_with(
            "UPDATE audio SET file_id = %s, caption = %s WHERE id = %s",
            ("new_fid", "new_cap", 1),
        )
        mock_conn.commit.assert_called_once()


def test_delete_audio(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection

    with patch("models.audios_model.get_connection", return_value=mock_conn):
        delete_audio(5)

        mock_cursor.execute.assert_called_once_with(
            "DELETE FROM audio WHERE id = %s", (5,)
        )
        mock_conn.commit.assert_called_once()
