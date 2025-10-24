import pytest
from unittest.mock import patch, MagicMock
from models.hadith_model import (
    HadithTableManager,
    save_id_and_content,
    edit_content,
    return_auto_content,
    mark_sent,
    get_status,
)


@pytest.fixture
def mock_conn_cursor():
    """اتصال و کرسر جعلی برای شبیه‌سازی پایگاه‌داده"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


def test_create_table(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.hadith_model.get_connection", return_value=mock_conn):
        db = HadithTableManager()
        db.create_table()
        mock_cursor.execute.assert_called_once()
        assert "CREATE TABLE IF NOT EXISTS hadith" in mock_cursor.execute.call_args[0][0]


def test_insert_row(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (None,)  # جدول خالی است

    with patch("models.hadith_model.get_connection", return_value=mock_conn):
        save_id_and_content(123, "Test content")

        # ابتدا SELECT MIN(sent) و بعد INSERT
        assert mock_cursor.execute.call_count == 2
        first_call, second_call = mock_cursor.execute.call_args_list
        assert "SELECT MIN(sent)" in first_call[0][0]
        assert "INSERT INTO hadith" in second_call[0][0]


def test_update_content(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.hadith_model.get_connection", return_value=mock_conn):
        edit_content(123, "New content")
        mock_cursor.execute.assert_called_once()
        assert "UPDATE hadith SET content" in mock_cursor.execute.call_args[0][0]
        assert mock_cursor.execute.call_args[0][1] == ("New content", 123)


def test_select_unsent(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = ("Hadith text", 1)
    with patch("models.hadith_model.get_connection", return_value=mock_conn):
        result = return_auto_content()
        mock_cursor.execute.assert_called_once()
        assert "SELECT content, id FROM hadith" in mock_cursor.execute.call_args[0][0]
        assert result == ("Hadith text", 1)
        
        
def test_update_sent_to_1(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.hadith_model.get_connection", return_value=mock_conn):
        mark_sent(1, "Some content")
        mock_cursor.execute.assert_called_once()
        assert "UPDATE hadith SET sent = 1" in mock_cursor.execute.call_args[0][0]
        assert mock_cursor.execute.call_args[0][1] == (1, "Some content")


def test_get_status_counts(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.side_effect = [(3,), (7,)]  # ابتدا unsent سپس sent
    with patch("models.hadith_model.get_connection", return_value=mock_conn):
        result = get_status()
        assert result == {"sent": 7, "unsent": 3}
        assert mock_cursor.execute.call_count == 2
