from models.database_connection import get_connection


class UserPermissionTableManager:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()

        self.cursor.close()
        self.conn.close()

    # -------------------------
    # اجرای امن
    # -------------------------
    def _execute(self, query, params=None, fetchone=False, fetchall=False):
        params = params or ()
        self.cursor.execute(query, params)

        if fetchone:
            return self.cursor.fetchone()
        if fetchall:
            return self.cursor.fetchall()

    # -------------------------
    # ساخت جدول user_permissions
    # -------------------------
    def _create_table(self):
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS user_permissions (
                user_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                UNIQUE (user_id, permission_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
            );
            """
        )

    # -------------------------
    # افزودن permission به کاربر
    # -------------------------
    def _add_permission_to_user(self, user_db_id, permission_id):
        self._execute(
            """
            INSERT INTO user_permissions (user_id, permission_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
            """,
            (user_db_id, permission_id),
        )

    # -------------------------
    # حذف permission از کاربر
    # -------------------------
    def _remove_permission_from_user(self, user_db_id, permission_id):
        self._execute(
            """
            DELETE FROM user_permissions
            WHERE user_id = %s AND permission_id = %s;
            """,
            (user_db_id, permission_id),
        )

    # -------------------------
    # گرفتن همه permission های کاربر
    # -------------------------
    def _get_user_permissions(self, user_db_id):
        return self._execute(
            """
            SELECT p.code 
            FROM permissions p
            JOIN user_permissions up ON up.permission_id = p.id
            WHERE up.user_id = %s
            ORDER BY p.code ASC;
            """,
            (user_db_id,),
            fetchall=True,
        )

    # -------------------------
    # چک داشتن permission خاص
    # -------------------------
    def _has_permission(self, user_db_id, permission_code):
        return (
            self._execute(
                """
            SELECT 1
            FROM permissions p
            JOIN user_permissions up ON up.permission_id = p.id
            WHERE up.user_id = %s AND p.code = %s;
            """,
                (user_db_id, permission_code),
                fetchone=True,
            )
            is not None
        )


def create_user_permission_table():
    with UserPermissionTableManager() as db:
        db._create_table()


def add_permission_to_user(user_db_id, permission_id):
    with UserPermissionTableManager() as db:
        db._add_permission_to_user(user_db_id, permission_id)


def remove_permission_from_user(user_db_id, permission_id):
    with UserPermissionTableManager() as db:
        db._remove_permission_from_user(user_db_id, permission_id)


def get_user_permissions(user_db_id):
    with UserPermissionTableManager() as db:
        return db._get_user_permissions(user_db_id)


def has_permission(user_db_id, permission_code):
    with UserPermissionTableManager() as db:
        return db._has_permission(user_db_id, permission_code)
