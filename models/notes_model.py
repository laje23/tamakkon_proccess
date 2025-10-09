from .database_connection import get_connection


class NoteTableManager:
    def __init__(self, conn=None):
        self.conn = conn or get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY,
                file_id TEXT DEFAULT NULL,
                media_type TEXT DEFAULT NULL,
                sent INTEGER DEFAULT 0 CHECK (sent IN (0,1))
            );
            """
        )

    def insert_text(self, text_id, file_id=None, media_type=None):
        self.cursor.execute(
            "INSERT INTO notes (id, file_id, media_type) VALUES (%s, %s, %s)",
            (text_id, file_id, media_type),
        )

    def text_exists(self, text_id):
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM notes WHERE id = %s)",
            (text_id,),
        )
        return self.cursor.fetchone()[0]

    def mark_sent(self, text_id):
        self.cursor.execute(
            "UPDATE notes SET sent = 1 WHERE id = %s",
            (text_id,),
        )

    def _get_unsent_note(self):
        self.cursor.execute(
            "SELECT id ,file_id, media_type FROM notes WHERE sent = 0 LIMIT 1"
        )
        return self.cursor.fetchone()

    def is_sent(self, text_id):
        self.cursor.execute(
            "SELECT sent FROM notes WHERE id = %s",
            (text_id,),
        )
        result = self.cursor.fetchone()
        return result and result[0] == 1

    def get_sent_stats(self):
        self.cursor.execute("SELECT COUNT(*) FROM notes WHERE sent = 1")
        sent = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM notes WHERE sent = 0")
        unsent = self.cursor.fetchone()[0]

        return {"sent": sent, "unsent": unsent}

    def update_media(self, text_id, file_id=None, media_type=None):
        self.cursor.execute(
            """
            UPDATE notes
            SET file_id = %s, media_type = %s
            WHERE id = %s
            """,
            (file_id, media_type, text_id),
        )


class TextPartManager:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS note_patrs (
                id SERIAL PRIMARY KEY,
                text_id INTEGER NOT NULL,
                part_index INTEGER NOT NULL,
                content TEXT NOT NULL,
                FOREIGN KEY (text_id) REFERENCES notes(id) ON DELETE CASCADE
            );
            """
        )

    def insert_part(self, text_id, part_index, content):
        self.cursor.execute(
            """
            INSERT INTO note_patrs (text_id, part_index, content)
            VALUES (%s, %s, %s)
            """,
            (text_id, part_index, content),
        )

    def get_parts(self, text_id):
        self.cursor.execute(
            """
            SELECT part_index, content FROM note_patrs
            WHERE text_id = %s
            ORDER BY part_index
            """,
            (text_id,),
        )
        return self.cursor.fetchall()

    def delete_parts(self, text_id):
        self.cursor.execute(
            "DELETE FROM note_patrs WHERE text_id = %s",
            (text_id,),
        )

    def update_part(self, part_id, content):
        self.cursor.execute(
            "UPDATE note_patrs SET content = %s WHERE id = %s",
            (content, part_id),
        )


# توابع سطح بالا مربوط به TextPartManager (بخش‌ها)


def create_table_parts():
    with TextPartManager() as db:
        db.create_table()


def save_part(text_id, part_index, content):
    with TextPartManager() as db:
        db.insert_part(text_id, part_index, content)


def get_parts(text_id):
    with TextPartManager() as db:
        return db.get_parts(text_id)


def delete_parts(text_id):
    with TextPartManager() as db:
        db.delete_parts(text_id)


def update_part(part_id, content):
    with TextPartManager() as db:
        db.update_part(part_id, content)


# توابع سطح بالا مربوط به NoteTableManager (متن‌ها)


def create_table():
    with NoteTableManager() as db:
        db.create_table()


def save_note(text_id, file_id=None, media_type=None):
    with NoteTableManager() as db:
        db.insert_text(text_id, file_id, media_type)


def check_is_exist(text_id):
    with NoteTableManager() as db:
        return db.text_exists(text_id)


def mark_sent(text_id):
    with NoteTableManager() as db:
        db.mark_sent(text_id)


def is_note_sent(text_id):
    with NoteTableManager() as db:
        return db.is_sent(text_id)


def get_status():
    with NoteTableManager() as db:
        return db.get_sent_stats()


def edit_media(text_id, file_id=None, media_type=None):
    with NoteTableManager() as db:
        db.update_media(text_id, file_id, media_type)


def get_unsent_note():
    with NoteTableManager() as db:
        return db._get_unsent_note()
