import pytest
from unittest.mock import MagicMock, patch

from models.qaa_collection_model import (
    CollectionsTable,
    create_collections_table,
    add_collection,
    get_all_collections,
    get_collection,
    delete_collection,
    collection_exists,
    activate_collection,
    deactivate_collection,
    update_collection_title,
    update_collection_description,
    edit_full_collection,
    get_collection_status,
    get_pos_collections,
)

# ---------- Fixture: Mock اتصال DB ----------
@pytest.fixture
def mock_db():
    with patch("models.qaa_collection_model.get_connection") as mock_conn_func:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn_func.return_value = mock_conn
        yield mock_cursor, mock_conn


# ---------- تست create table ----------
def test_create_collections_table(mock_db):
    cursor, conn = mock_db

    create_collections_table()

    sql = cursor.execute.call_args_list[0][0][0]
    assert "CREATE TABLE IF NOT EXISTS collections" in sql
    conn.commit.assert_called_once()


# ---------- تست insert ----------
def test_add_collection(mock_db):
    cursor, conn = mock_db
    cursor.fetchone.return_value = (5,)

    collection_id = add_collection("کالکشن تست", "توضیح")

    # بررسی SQL
    sql = cursor.execute.call_args_list[0][0][0]
    params = cursor.execute.call_args_list[0][0][1]

    assert "INSERT INTO collections" in sql
    assert params == ("کالکشن تست", "توضیح")
    assert collection_id == 5
    conn.commit.assert_called_once()



# ---------- تست get all ----------
def test_get_all_collections(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [
        (1, "A", None, 0),
        (2, "B", "desc", 1),
    ]

    result = get_all_collections()

    sql = cursor.execute.call_args[0][0]
    assert "SELECT id, title, description, is_active FROM collections" in sql
    assert len(result) == 2


# ---------- تست get by id ----------
def test_get_collection(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = (3, "C", None, 1)

    result = get_collection(3)

    sql, params = cursor.execute.call_args[0]
    assert params == (3,)
    assert result[0] == 3


# ---------- تست delete ----------
def test_delete_collection(mock_db):
    cursor, conn = mock_db

    delete_collection(9)

    cursor.execute.assert_any_call(
        "DELETE FROM collections WHERE id = %s",
        (9,),
    )
    conn.commit.assert_called_once()


# ---------- تست exists ----------
def test_collection_exists_true(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = (7,)

    result = collection_exists("کالکشن")

    assert result == 7


def test_collection_exists_false(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = None

    result = collection_exists("کالکشن")

    assert result is None


# ---------- تست activate / deactivate ----------
def test_activate_collection(mock_db):
    cursor, conn = mock_db

    activate_collection(4)

    cursor.execute.assert_any_call(
        "UPDATE collections SET is_active = 1 WHERE id = %s",
        (4,),
    )
    conn.commit.assert_called_once()


def test_deactivate_collection(mock_db):
    cursor, conn = mock_db

    deactivate_collection(4)

    cursor.execute.assert_any_call(
        "UPDATE collections SET is_active = 0 WHERE id = %s",
        (4,),
    )
    conn.commit.assert_called_once()


# ---------- تست update title ----------
def test_update_collection_title(mock_db):
    cursor, conn = mock_db

    update_collection_title(2, "عنوان جدید")

    cursor.execute.assert_any_call(
        "UPDATE collections SET title = %s WHERE id = %s",
        ("عنوان جدید", 2),
    )
    conn.commit.assert_called_once()


# ---------- تست update description ----------
def test_update_collection_description(mock_db):
    cursor, conn = mock_db

    update_collection_description(2, "توضیح جدید")

    cursor.execute.assert_any_call(
        "UPDATE collections SET description = %s WHERE id = %s",
        ("توضیح جدید", 2),
    )
    conn.commit.assert_called_once()


# ---------- تست update همه فیلدها ----------
def test_edit_full_collection(mock_db):
    cursor, conn = mock_db

    edit_full_collection(1, "T", "D", True)

    sql = cursor.execute.call_args_list[0][0][0]
    params = cursor.execute.call_args_list[0][0][1]

    assert "UPDATE collections" in sql
    assert params == ("T", "D", 1, 1)
    conn.commit.assert_called_once()


# ---------- تست get status ----------
def test_get_collection_status(mock_db):
    cursor, _ = mock_db
    cursor.fetchone.return_value = (1,)

    status = get_collection_status(10)

    assert status == 1


# ---------- تست get active / inactive ----------
def test_get_pos_collections_active(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [(1, "A", None)]

    result = get_pos_collections(True)

    sql, params = cursor.execute.call_args[0]
    assert params == (1,)
    assert len(result) == 1


def test_get_pos_collections_inactive(mock_db):
    cursor, _ = mock_db
    cursor.fetchall.return_value = [(2, "B", None)]

    result = get_pos_collections(False)

    sql, params = cursor.execute.call_args[0]
    assert params == (0,)
    assert len(result) == 1


# ---------- تست rollback در صورت exception ----------
def test_context_manager_rollback_on_error(mock_db):
    cursor, conn = mock_db

    with pytest.raises(Exception):
        with CollectionsTable() as db:
            raise Exception("DB Error")

    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
