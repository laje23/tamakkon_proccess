from models.database_connection import get_connection


class UserTableManager:
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
    # ساخت جدول
    # -------------------------
    def _create_table(self):
        self._execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                phone_number BIGINT,
                is_admin SMALLINT DEFAULT 0
            );
            """
        )

    # -------------------------
    # افزودن کاربر
    # -------------------------
    def _add_user(self, user_id, name, phone_number=None, is_admin=0):
        return self._execute(
            """
            INSERT INTO users (user_id, name, phone_number, is_admin)
            VALUES (%s, %s, %s, %s)
            RETURNING id;
            """,
            (user_id, name, phone_number, is_admin),
            fetchone=True,
        )

    # -------------------------
    # گرفتن کاربر
    # -------------------------
    def _get_user(self, user_id):
        return self._execute(
            """
            SELECT id, user_id, name, phone_number, is_admin
            FROM users
            WHERE user_id = %s;
            """,
            (user_id,),
            fetchone=True,
        )

    # -------------------------
    # گرفتن همه کاربران
    # -------------------------
    def _get_all_users(self):
        return self._execute(
            """
            SELECT id, user_id, name, phone_number, is_admin
            FROM users
            ORDER BY id ASC;
            """,
            fetchall=True,
        )

    # -------------------------
    # آپدیت نام
    # -------------------------
    def _update_name(self, user_id, new_name):
        self._execute(
            """
            UPDATE users
            SET name = %s
            WHERE user_id = %s;
            """,
            (new_name, user_id),
        )

    # -------------------------
    # آپدیت شماره
    # -------------------------
    def _update_phone(self, user_id, new_phone_number):
        self._execute(
            """
            UPDATE users
            SET phone_number = %s
            WHERE user_id = %s;
            """,
            (new_phone_number, user_id),
        )

    # -------------------------
    # ست کردن مقدار is_admin (0 یا 1)
    # -------------------------
    def _set_admin(self, user_id, is_admin: int):
        self._execute(
            """
            UPDATE users
            SET is_admin = %s
            WHERE user_id = %s;
            """,
            (is_admin, user_id),
        )

    # -------------------------
    # حذف کاربر
    # -------------------------
    def _delete_user(self, user_id):
        self._execute(
            """
            DELETE FROM users
            WHERE user_id = %s;
            """,
            (user_id,),
        )


# -------------------------
# توابع بیرون کلاس
# -------------------------


def create_table():
    with UserTableManager() as db:
        db._create_table()


def add_user(user_id, name, phone_number=None, is_admin=0):
    with UserTableManager() as db:
        return db._add_user(user_id, name, phone_number, is_admin)


def get_user(user_id):
    with UserTableManager() as db:
        return db._get_user(user_id)


def get_all_users():
    with UserTableManager() as db:
        return db._get_all_users()


def update_name(user_id, new_name):
    with UserTableManager() as db:
        db._update_name(user_id, new_name)


def update_phone(user_id, new_phone_number):
    with UserTableManager() as db:
        db._update_phone(user_id, new_phone_number)


def set_admin(user_id, is_admin: int):
    with UserTableManager() as db:
        db._set_admin(user_id, is_admin)


def delete_user(user_id):
    with UserTableManager() as db:
        db._delete_user(user_id)
