import pytest
from unittest.mock import MagicMock, patch

from models.qaa_result_model import (
    GameResultsTable,
    create_results_table,
    add_result,
    get_user_results,
    get_collection_results,
    get_collection_winners,
    get_collection_losers,
    delete_result,
)

# ---------- Fixture: Mock اتصال DB ----------
@pytest.fixture
def mock_db():
    with patch("models.qaa_result_model.get_connection") as mock_conn_func:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_func.return_value = mock_conn
        yield mock_cursor, mock_conn


# ---------- تست create_results_table ----------
def test_create_results_table(mock_db):
    cursor, conn = mock_db
    create_results_table()

    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS game_results" in sql
    conn.commit.assert_called_once()


# ---------- تست insert_result ----------
def test_add_result(mock_db):
    cursor, conn = mock_db
    cursor.fetchone.return_value = (42,)

    result_id = add_result(10, 3, 1)

    cursor.execute.assert_called_once()
    sql, params = cursor.execute.call_args[0]

    assert "INSERT INTO game_results" in sql
    assert params == (10, 3, 1)
    assert result_id == 42
    conn.commit.assert_called_once()


# ---------- تست get_user_results ----------
def test_get_user_results(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [
        (1, 10, 3, 1),
        (2, 10, 3, 0),
    ]

    results = get_user_results(10)

    sql, params = cursor.execute.call_args[0]
    assert "WHERE user_id = %s" in sql
    assert params == (10,)
    assert len(results) == 2


# ---------- تست get_collection_results ----------
def test_get_collection_results(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [(1, 11, 3, 1)]

    results = get_collection_results(3)

    sql, params = cursor.execute.call_args[0]
    assert "WHERE collection_id = %s" in sql
    assert params == (3,)
    assert results[0][2] == 3


# ---------- تست get_collection_winners ----------
def test_get_collection_winners(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [(1, 10)]

    results = get_collection_winners(5)

    sql, params = cursor.execute.call_args[0]
    assert "is_winner = %s" in sql
    assert params == (5, 1)
    assert len(results) == 1


# ---------- تست get_collection_losers ----------
def test_get_collection_losers(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [(2, 12)]

    results = get_collection_losers(5)

    sql, params = cursor.execute.call_args[0]
    assert params == (5, 0)
    assert len(results) == 1


# ---------- تست delete_result ----------
def test_delete_result(mock_db):
    cursor, conn = mock_db

    delete_result(99)

    cursor.execute.assert_called_once_with(
        "DELETE FROM game_results WHERE id = %s",
        (99,),
    )
    conn.commit.assert_called_once()


# ---------- تست rollback در صورت exception ----------
def test_context_manager_rollback_on_error(mock_db):
    cursor, conn = mock_db

    with pytest.raises(Exception):
        with GameResultsTable() as db:
            raise Exception("DB Error")

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
