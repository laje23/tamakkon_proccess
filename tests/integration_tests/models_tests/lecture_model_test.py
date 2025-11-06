import pytest
from unittest.mock import patch, MagicMock
from models.lectures_model import (
    LecturesTable,
    save_lecture,
    mark_lecture_sent,
    auto_return_lecture,
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
    with patch("models.lectures_model.get_connection", return_value=mock_conn):
        db = LecturesTable()
        db._create_table()
        mock_cursor.execute.assert_called_once()
        assert "CREATE TABLE IF NOT EXISTS lectures" in mock_cursor.execute.call_args[0][0]


def test_insert_row(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (None,)  # جدول خالی است

    with patch("models.lectures_model.get_connection", return_value=mock_conn):
        save_lecture("file_123", "Lecture caption")

        # ابتدا SELECT MIN(sent) و بعد INSERT
        assert mock_cursor.execute.call_count == 2
        first_call, second_call = mock_cursor.execute.call_args_list
        assert "SELECT MIN(sent)" in first_call[0][0]
        assert "INSERT INTO lectures" in second_call[0][0]


def test_select_auto_file_id(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (1, "file_abc", "caption text")

    with patch("models.lectures_model.get_connection", return_value=mock_conn):
        result = auto_return_lecture()
        mock_cursor.execute.assert_called_once()
        query = mock_cursor.execute.call_args[0][0].replace("\n", " ")
        assert "SELECT id, file_id, caption FROM lectures" in query
        assert result == (1, "file_abc", "caption text")


def test_increment_sent(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.lectures_model.get_connection", return_value=mock_conn):
        mark_lecture_sent(5)
        mock_cursor.execute.assert_called_once_with(
            "UPDATE lectures SET sent = sent + 1 WHERE id = %s",
            (5,),
        )


def test_get_sent_unsent_counts(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.side_effect = [(3,), (7,)]  # ابتدا unsent سپس sent

    with patch("models.lectures_model.get_connection", return_value=mock_conn):
        result = get_status()
        assert result == {"sent": 7, "unsent": 3}
        assert mock_cursor.execute.call_count == 2
