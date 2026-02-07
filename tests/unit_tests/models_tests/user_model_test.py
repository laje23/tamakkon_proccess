import pytest
from unittest.mock import MagicMock, patch
import re
from models.user_model import (
    UserTableManager,
    create_table,
    add_user,
    get_user,
    get_all_users,
    update_name,
    update_phone,
    delete_user,
)


# ---------- Fixture برای mock اتصال DB ----------
@pytest.fixture
def mock_db():
    with patch("models.user_model.get_connection") as mock_conn_func:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_func.return_value = mock_conn
        yield mock_cursor, mock_conn


# ---------- تست create_table ----------
def test_create_table(mock_db):
    cursor, conn = mock_db
    create_table()
    sql = cursor.execute.call_args[0][0]
    assert "CREATE TABLE IF NOT EXISTS users" in sql
    conn.commit.assert_called_once()


# ---------- تست add_user ----------
def test_add_user(mock_db):
    cursor, conn = mock_db
    cursor.fetchone.return_value = (42,)  # return id
    user_id = add_user(1234, "Ali", 989123456789, 1)
    sql, params = cursor.execute.call_args[0]
    assert "INSERT INTO users" in sql
    assert params == (1234, "Ali", 989123456789, 1)
    assert user_id[0] == 42
    conn.commit.assert_called_once()


# ---------- تست get_user ----------
def test_get_user(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = (1, 1234, "Ali", 989123456789, 1)
    result = get_user(1234)
    sql, params = cursor.execute.call_args[0]
    assert "SELECT id, user_id, name, phone_number, is_admin" in sql
    assert params == (1234,)
    assert result[1] == 1234


# ---------- تست get_all_users ----------
def test_get_all_users(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [
        (1, 1234, "Ali", 989123456789, 1),
        (2, 5678, "Sara", None, 0),
    ]
    results = get_all_users()
    sql, _ = cursor.execute.call_args[0]
    assert "SELECT id, user_id, name, phone_number, is_admin" in sql
    assert len(results) == 2


# ---------- تست update_name ----------


def test_update_name(mock_db):
    cursor, conn = mock_db
    update_name(1234, "Mohammad")
    sql, params = cursor.execute.call_args[0]
    assert re.search(r"UPDATE\s+users\s+SET\s+name", sql)
    assert params == ("Mohammad", 1234)
    conn.commit.assert_called_once()


def test_update_phone(mock_db):
    cursor, conn = mock_db
    update_phone(1234, 989112233445)
    sql, params = cursor.execute.call_args[0]
    assert re.search(r"UPDATE\s+users\s+SET\s+phone_number", sql)
    assert params == (989112233445, 1234)
    conn.commit.assert_called_once()


# ---------- تست delete_user ----------
def test_delete_user(mock_db):
    cursor, conn = mock_db
    delete_user(1234)
    sql, params = cursor.execute.call_args[0]
    assert "DELETE FROM users" in sql
    assert params == (1234,)
    conn.commit.assert_called_once()


# ---------- تست rollback در صورت Exception ----------
def test_context_manager_rollback_on_error(mock_db):
    cursor, conn = mock_db
    with pytest.raises(Exception):
        with UserTableManager() as db:
            raise Exception("DB Error")
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
