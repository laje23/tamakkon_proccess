import pytest
from unittest.mock import MagicMock, patch

from models.qaa_questions_model import (
    QuestionsTable,
    create_questions_table,
    add_question,
    get_question,
    get_all_question_by_collection_id,
    get_question_by_id,
    get_all_questions,
    get_question_count,
    update_question_text,
    update_option1,
    update_option2,
    update_option3,
    update_correct,
    update_question_collection,
    update_question_index,
)


# ---------- Fixture: Mock اتصال DB ----------
@pytest.fixture
def mock_db():
    with patch("models.qaa_questions_model.get_connection") as mock_conn_func:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_func.return_value = mock_conn
        yield mock_cursor, mock_conn


# ---------- تست create_questions_table ----------
def test_create_questions_table(mock_db):
    cursor, conn = mock_db
    create_questions_table()
    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS questions" in sql
    conn.commit.assert_called_once()


# ---------- تست add_question ----------
def test_add_question(mock_db):
    cursor, conn = mock_db

    # Mock get_next_index و insert_row
    cursor.fetchone.side_effect = [(1,), (7,)]  # اول برای index، دوم برای id

    question_id = add_question(3, "سوال", "a", "b", "c", "a")

    # execute دوم مربوط به INSERT است
    sql, params = cursor.execute.call_args_list[1][0]

    assert "INSERT INTO questions" in sql
    assert params == (3, 1, "سوال", "a", "b", "c", "a")
    assert question_id == 7
    conn.commit.assert_called_once()


# ---------- تست get_question ----------
def test_get_question(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = (1, 3, 1, "Q", "a", "b", "c", "a")
    result = get_question(3, 1)
    sql, params = cursor.execute.call_args[0]
    assert "WHERE collection_id = %s AND question_index = %s" in sql
    assert params == (3, 1)
    assert result[2] == 1


# ---------- تست get_all_question_by_collection_id ----------
def test_get_all_question_by_collection_id(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [(1, 3, 1, "Q", "a", "b", "c", "a")]
    results = get_all_question_by_collection_id(3)
    sql, params = cursor.execute.call_args[0]
    assert "WHERE collection_id = %s" in sql
    assert params == (3,)
    assert len(results) == 1


# ---------- تست get_question_by_id ----------
def test_get_question_by_id(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = (1, 3, 1, "Q", "a", "b", "c", "a")
    result = get_question_by_id(1)
    sql, params = cursor.execute.call_args[0]
    assert "WHERE id = %s" in sql
    assert params == (1,)
    assert result[0] == 1


# ---------- تست get_question_count ----------
def test_get_question_count(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = (5,)
    count = get_question_count(3)
    sql, params = cursor.execute.call_args[0]
    assert "SELECT COUNT(*) FROM questions" in sql
    assert params == (3,)
    assert count == 5


# ---------- تست update متدها ----------
@pytest.mark.parametrize(
    "update_func,expected_sql",
    [
        (update_question_text, "UPDATE questions SET question_text = %s"),
        (update_option1, "UPDATE questions SET option1 = %s"),
        (update_option2, "UPDATE questions SET option2 = %s"),
        (update_option3, "UPDATE questions SET option3 = %s"),
        (update_correct, "UPDATE questions SET correct = %s"),
        (update_question_collection, "UPDATE questions SET collection_id = %s"),
        (update_question_index, "UPDATE questions SET question_index = %s"),
    ],
)
def test_update_functions(mock_db, update_func, expected_sql):
    cursor, conn = mock_db
    update_func(1, "test")
    sql, params = cursor.execute.call_args[0]
    assert expected_sql in sql
    assert params[1] == 1
    conn.commit.assert_called_once()


# ---------- تست rollback هنگام exception ----------
def test_context_manager_rollback_on_error(mock_db):
    cursor, conn = mock_db
    with pytest.raises(Exception):
        with QuestionsTable() as db:
            raise Exception("DB error")
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
