from models.database_connection import get_connection

class MediaTableManager:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS media (
                id SERIAL PRIMARY KEY,
                file_id TEXT NOT NULL,
                type TEXT NOT NULL
            );
            """
        )

    def get_media_by_id(self, id):
        self.cursor.execute("SELECT * FROM media WHERE id = %s", (id,))
        return self.cursor.fetchone()

    # ---------- Generic CRUD ----------

    def insert(self, file_id, media_type):
        self.cursor.execute(
            """
            INSERT INTO media (file_id, type)
            VALUES (%s, %s)
            RETURNING id
            """,
            (file_id, media_type),
        )
        media_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return media_id

    def update(self, id, file_id=None, media_type=None):
        if file_id is not None:
            self.cursor.execute(
                "UPDATE media SET file_id = %s WHERE id = %s",
                (file_id, id),
            )
        if media_type is not None:
            self.cursor.execute(
                "UPDATE media SET type = %s WHERE id = %s",
                (media_type, id),
            )

    def delete(self, id):
        self.cursor.execute("DELETE FROM media WHERE id = %s", (id,))

    def select_by_id(self, id):
        self.cursor.execute(
            "SELECT id, file_id, type FROM media WHERE id = %s",
            (id,),
        )
        return self.cursor.fetchone()

    def select_all_by_type(self, media_type):
        self.cursor.execute(
            """
            SELECT id, file_id FROM media
            WHERE type = %s
            ORDER BY id DESC
            """,
            (media_type,),
        )
        return self.cursor.fetchall()

    def select_auto_by_type(self, media_type):
        self.cursor.execute(
            """
            SELECT id, file_id FROM media
            WHERE type = %s
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (media_type,),
        )
        return self.cursor.fetchone()

    def exists(self, id):
        self.cursor.execute("SELECT 1 FROM media WHERE id = %s", (id,))
        return self.cursor.fetchone() is not None

    def get_last_id_by_type(self, media_type):
        self.cursor.execute(
            "SELECT MAX(id) FROM media WHERE type = %s",
            (media_type,),
        )
        result = self.cursor.fetchone()
        return result[0] if result and result[0] else None


# ---------- Table helpers ----------

def create_table():
    with MediaTableManager() as db:
        db.create_table()


