from models.database_connection import get_connection


class CollectionsTable:
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

    def _create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS collections (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                is_active SMALLINT NOT NULL DEFAULT 0
            );
            """
        )

    # -----------------------------
    # افزودن رکورد جدید
    # -----------------------------
    def insert_row(self, title, description=None):
        self.cursor.execute(
            """
            INSERT INTO collections (title, description, is_active)
            VALUES (%s, %s, 0)
            RETURNING id
            """,
            (title, description),
        )
        return self.cursor.fetchone()[0]

    # -----------------------------
    # گرفتن همه رکوردها
    # -----------------------------
    def get_all(self):
        self.cursor.execute(
            "SELECT id, title, description, is_active FROM collections ORDER BY id"
        )
        return self.cursor.fetchall()

    # -----------------------------
    # بررسی وجود عنوان
    # -----------------------------
    def exists(self, title):
        self.cursor.execute(
            "SELECT id FROM collections WHERE title = %s LIMIT 1",
            (title,),
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    # -----------------------------
    # گرفتن یک رکورد با id
    # -----------------------------
    def get_by_id(self, id):
        self.cursor.execute(
            "SELECT id, title, description, is_active FROM collections WHERE id = %s",
            (id,),
        )
        return self.cursor.fetchone()

    # -----------------------------
    # حذف رکورد
    # -----------------------------
    def delete(self, id):
        self.cursor.execute("DELETE FROM collections WHERE id = %s", (id,))

    # -----------------------------
    # فعال / غیرفعال کردن
    # -----------------------------
    def activate(self, id):
        self.cursor.execute("UPDATE collections SET is_active = 1 WHERE id = %s", (id,))

    def deactivate(self, id):
        self.cursor.execute("UPDATE collections SET is_active = 0 WHERE id = %s", (id,))

    # -----------------------------
    # ویرایش تک‌ستونی 👇
    # -----------------------------
    def update_title(self, id, new_title):
        self.cursor.execute(
            "UPDATE collections SET title = %s WHERE id = %s",
            (new_title, id),
        )

    def update_description(self, id, description):
        self.cursor.execute(
            "UPDATE collections SET description = %s WHERE id = %s",
            (description, id),
        )

    # -----------------------------
    # گرفتن وضعیت فعال بودن
    # -----------------------------
    def get_status(self, id):
        self.cursor.execute("SELECT is_active FROM collections WHERE id = %s", (id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    # -----------------------------
    # گرفتن فقط فعال یا غیرفعال‌ها
    # -----------------------------
    def get_active_collections(self, st):
        self.cursor.execute(
            "SELECT id, title, description FROM collections WHERE is_active = %s ORDER BY id",
            (st,),
        )
        return self.cursor.fetchall()

    # -----------------------------
    # ویرایش تمام فیلدها باهم (اختیاری ولی کاربردی)
    # -----------------------------
    def update_all_fields(self, id, title, description, is_active):
        self.cursor.execute(
            """
            UPDATE collections
            SET title = %s,
                description = %s,
                is_active = %s
            WHERE id = %s
            """,
            (title, description, is_active, id),
        )


# ------------------ توابع خارج از کلاس ------------------ #


def create_collections_table():
    with CollectionsTable() as db:
        db._create_table()


def add_collection(title, description=None):
    with CollectionsTable() as db:
        return db.insert_row(title, description)


def get_all_collections():
    with CollectionsTable() as db:
        return db.get_all()


def get_collection(id):
    with CollectionsTable() as db:
        return db.get_by_id(id)


def delete_collection(id):
    with CollectionsTable() as db:
        db.delete(id)


def collection_exists(title):
    with CollectionsTable() as db:
        return db.exists(title)


def activate_collection(id):
    with CollectionsTable() as db:
        db.activate(id)


def deactivate_collection(id):
    with CollectionsTable() as db:
        db.deactivate(id)


def update_collection_title(id, title):
    with CollectionsTable() as db:
        db.update_title(id, title)


def update_collection_description(id, description):
    with CollectionsTable() as db:
        db.update_description(id, description)


def update_collection_status(id, active: bool):
    with CollectionsTable() as db:
        db.update_status(id, active)


def edit_full_collection(id, title, description, active):
    with CollectionsTable() as db:
        db.update_all_fields(id, title, description, 1 if active else 0)


def get_collection_status(id):
    with CollectionsTable() as db:
        return db.get_status(id)


def get_pos_collections(active: bool = False):
    with CollectionsTable() as db:
        return db.get_active_collections(1 if active else 0)
