import pytest
from unittest.mock import patch, MagicMock
from models.books_model import (
    BooksTableManager,
    save_book,
    edit_book,
    get_unsent_book,
    mark_book_sent,
    get_status,
    check_book_exists,
)

@pytest.fixture
def mock_db_connection():
    """اتصال و کرسر جعلی برای شبیه‌سازی پایگاه‌داده"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


def test_save_book(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch("models.books_model.get_connection", return_value=mock_conn):
        save_book("Book A", "Author A", "Pub A", "Excerpt A")

        mock_cursor.execute.assert_called_once_with(
            """
            INSERT INTO books (title, author, publisher, excerpt, sent)
            VALUES (%s, %s, %s, %s, 0)
        """,
            ("Book A", "Author A", "Pub A", "Excerpt A"),
        )
        mock_conn.commit.assert_called_once()


def test_edit_book(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch("models.books_model.get_connection", return_value=mock_conn):
        edit_book(1, "Updated Title", "Updated Author", "Updated Pub", "Updated Excerpt")

        mock_cursor.execute.assert_called_once_with(
            """
            UPDATE books
            SET title = %s,
                author = %s,
                publisher = %s,
                excerpt = %s
            WHERE id = %s
        """,
            ("Updated Title", "Updated Author", "Updated Pub", "Updated Excerpt", 1),
        )
        mock_conn.commit.assert_called_once()


def test_get_unsent_book(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = (1, "Book X", "Author X", "Pub X", "Excerpt X")

    with patch("models.books_model.get_connection", return_value=mock_conn):
        result = get_unsent_book()

        mock_cursor.execute.assert_called_once()
        assert result == {
            "id": 1,
            "title": "Book X",
            "author": "Author X",
            "publisher": "Pub X",
            "excerpt": "Excerpt X",
        }


def test_mark_book_sent(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    with patch("models.books_model.get_connection", return_value=mock_conn):
        mark_book_sent(5)

        mock_cursor.execute.assert_called_once_with(
            "UPDATE books SET sent = 1 WHERE id = %s", (5,)
        )
        mock_conn.commit.assert_called_once()


def test_get_status(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    # دو بار fetchone صدا زده می‌شود: یکی برای sent و یکی برای unsent
    mock_cursor.fetchone.side_effect = [(3,), (7,)]

    with patch("models.books_model.get_connection", return_value=mock_conn):
        result = get_status()

        assert result == {"sent": 3, "unsent": 7}
        assert mock_cursor.execute.call_count == 2
        mock_conn.commit.assert_called_once()


def test_check_book_exists(mock_db_connection):
    mock_conn, mock_cursor = mock_db_connection
    mock_cursor.fetchone.return_value = [True]

    with patch("models.books_model.get_connection", return_value=mock_conn):
        result = check_book_exists(1)

        mock_cursor.execute.assert_called_once_with(
            "SELECT EXISTS(SELECT 1 FROM books WHERE id = %s)", (1,)
        )
        assert result is True
