import pytest
from unittest.mock import patch, MagicMock
from models.clips_model import ClipsTable, save_clip, mark_clip_sent, get_status, auto_return_file_id


@pytest.fixture
def mock_conn_cursor():
    """ماک کردن اتصال و کرسر دیتابیس"""
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


def test_create_table(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        db._create_table()
        mock_cursor.execute.assert_called_once()
        assert "CREATE TABLE IF NOT EXISTS clips" in mock_cursor.execute.call_args[0][0]


def test_insert_row(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.side_effect = [(None,)]  # برای اولین بار مقدار None برمی‌گرداند

    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        db.insert_row("file123", "caption text")

        # دو بار کوئری اجرا می‌شود: یکی برای min(sent) و یکی برای insert
        assert mock_cursor.execute.call_count == 2
        args_list = [call[0][0] for call in mock_cursor.execute.call_args_list]
        assert "SELECT MIN(sent)" in args_list[0]
        assert "INSERT INTO clips" in args_list[1]


def test_edit_caption(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        db.edit_caption(10, "new caption")
        mock_cursor.execute.assert_called_once()
        assert "UPDATE clips SET caption" in mock_cursor.execute.call_args[0][0]
        assert mock_cursor.execute.call_args[0][1] == ("new caption", 10)


def test_select_auto_file_id(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (1, "file_abc", "test_caption")

    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        result = db.select_auto_file_id()

        mock_cursor.execute.assert_called_once()
        assert "SELECT id, file_id, caption FROM clips" in mock_cursor.execute.call_args[0][0]
        assert result == (1, "file_abc", "test_caption")


def test_increment_sent(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        db.increment_sent(5)
        mock_cursor.execute.assert_called_once_with(
            "UPDATE clips SET sent = sent + 1 WHERE id = %s",
            (5,),
        )


def test_get_sent_unsent_counts(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.side_effect = [(2,), (5,)]  # اول unsent بعد sent

    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        result = db.get_sent_unsent_counts()

        assert result == {"sent": 5, "unsent": 2}
        assert mock_cursor.execute.call_count == 2


def test_clip_exists(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (1,)
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        assert db.clip_exists(1) is True

    mock_cursor.fetchone.return_value = None
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        assert db.clip_exists(99) is False


def test_is_clip_sent(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (2,)
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        assert db._is_clip_sent(1) is True

    mock_cursor.fetchone.return_value = (0,)
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        assert db._is_clip_sent(2) is False


def test_get_last_clip_id(mock_conn_cursor):
    mock_conn, mock_cursor = mock_conn_cursor
    mock_cursor.fetchone.return_value = (42,)
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        assert db.get_last_clip_id() == 42

    mock_cursor.fetchone.return_value = (None,)
    with patch("models.clips_model.get_connection", return_value=mock_conn):
        db = ClipsTable()
        assert db.get_last_clip_id() is None
