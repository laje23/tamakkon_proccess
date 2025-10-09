from models.database_connection import get_connection


class AudioTableManager:
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
            CREATE TABLE IF NOT EXISTS audio (
                id SERIAL PRIMARY KEY,
                filename TEXT DEFAULT NULL,
                file_id TEXT NOT NULL,
                caption TEXT DEFAULT NULL 
            );
            """
        )

    def insert_row(self, filename, file_id, caption=None):
        self.cursor.execute(
            "INSERT INTO audio (filename, file_id, caption) VALUES (%s, %s, %s)",
            (filename, file_id, caption),
        )

    def return_content_by_id(self, id):
        self.cursor.execute(
            """SELECT file_id, caption FROM audio WHERE id = %s LIMIT 1""", (id,)
        )
        result = self.cursor.fetchone()
        return result if result else None

    def change_row_by_id(self, id, file_id, caption):
        self.cursor.execute(
            "UPDATE audio SET file_id = %s, caption = %s WHERE id = %s",
            (file_id, caption, id),
        )

    def get_all_rows(self):
        self.cursor.execute("SELECT id, filename, file_id, caption FROM audio")
        return self.cursor.fetchall()

    def delete_row_by_id(self, id):
        self.cursor.execute("DELETE FROM audio WHERE id = %s", (id,))


# --- Wrapper functions ---
def create_table():
    with AudioTableManager() as db:
        db.create_table()


def insert_audio(filename, file_id, caption=None):
    with AudioTableManager() as db:
        return db.insert_row(filename, file_id, caption)


def update_row_by_id(id, file_id, caption):
    with AudioTableManager() as db:
        db.change_row_by_id(id, file_id, caption)


def get_file_id_and_caption_by_id(id):
    with AudioTableManager() as db:
        return db.return_content_by_id(id)


def get_all_audios():
    with AudioTableManager() as db:
        return db.get_all_rows()


def delete_audio(id):
    with AudioTableManager() as db:
        db.delete_row_by_id(id)
