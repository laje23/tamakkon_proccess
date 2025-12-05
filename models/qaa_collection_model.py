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
                is_active SMALLINT NOT NULL DEFAULT 0
            );
            """
        )

    def insert_row(self, title):
        self.cursor.execute(
            """
            INSERT INTO collections (title, is_active)
            VALUES (%s, 0)
            RETURNING id
            """,
            (title,),
        )
        return self.cursor.fetchone()[0]

    def get_all(self):
        self.cursor.execute("SELECT id, title, is_active FROM collections ORDER BY id")
        return self.cursor.fetchall()

    def exists(self, title):
        self.cursor.execute(
            "SELECT id FROM collections WHERE title = %s LIMIT 1", (title,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_by_id(self, id):
        self.cursor.execute(
            "SELECT id, title, is_active FROM collections WHERE id = %s", (id,)
        )
        return self.cursor.fetchone()

    def delete(self, id):
        self.cursor.execute("DELETE FROM collections WHERE id = %s", (id,))

    def activate(self, id):
        self.cursor.execute("UPDATE collections SET is_active = 1 WHERE id = %s", (id,))

    def deactivate(self, id):
        self.cursor.execute("UPDATE collections SET is_active = 0 WHERE id = %s", (id,))

    def get_status(self, id):
        self.cursor.execute("SELECT is_active FROM collections WHERE id = %s", (id,))
        row = self.cursor.fetchone()
        return row[0] if row else None

    def get_active_collections(self, st):
        self.cursor.execute(
            "SELECT id, title FROM collections WHERE is_active = %s ORDER BY id", (st,)
        )
        return self.cursor.fetchall()


def create_collections_table():
    with CollectionsTable() as db:
        db._create_table()


def add_collection(title):
    with CollectionsTable() as db:
        return db.insert_row(title)


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


def get_collection_status(id):
    with CollectionsTable() as db:
        return db.get_status(id)


def get_pos_collections(active: bool = False):
    if active:
        with CollectionsTable() as db:
            return db.get_active_collections(1)
    else:
        with CollectionsTable() as db:
            return db.get_active_collections(0)
