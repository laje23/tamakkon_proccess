from models.database_connection import get_connection


class CollectionsTable:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def _create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS collections (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL
            );
            """
        )

    def insert_row(self, title):
        self.cursor.execute(
            "INSERT INTO collections (title) VALUES (%s) RETURNING id",
            (title,)
        )
        new_id = self.cursor.fetchone()[0]
        return new_id


    def get_all(self):
        self.cursor.execute("SELECT id, title FROM collections ORDER BY id")
        return self.cursor.fetchall()
    
    def exists(self, title):
        self.cursor.execute(
            "SELECT id FROM collections WHERE title = %s LIMIT 1",
            (title,)
        )
        row = self.cursor.fetchone()
        return row[0] if row else None



    def get_by_id(self, id):
        self.cursor.execute(
            "SELECT id, title FROM collections WHERE id = %s",
            (id,)
        )
        return self.cursor.fetchone()

    def delete(self, id):
        self.cursor.execute("DELETE FROM collections WHERE id = %s", (id,))


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
