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
                filename TEXT,
                file_id TEXT NOT NULL,
                caption TEXT,
                type TEXT NOT NULL,
                sent INTEGER DEFAULT 0 CHECK (sent >= 0)
            );
            """
        )

    # ---------- Generic CRUD ----------

    def insert(self, filename, file_id, caption, media_type, sent=0):
        self.cursor.execute(
            """
            INSERT INTO media (filename, file_id, caption, type, sent)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (filename, file_id, caption, media_type, sent),
        )

    def update(self, id, file_id=None, caption=None):
        if file_id is not None:
            self.cursor.execute(
                "UPDATE media SET file_id = %s WHERE id = %s",
                (file_id, id),
            )
        if caption is not None:
            self.cursor.execute(
                "UPDATE media SET caption = %s WHERE id = %s",
                (caption, id),
            )

    def delete(self, id):
        self.cursor.execute("DELETE FROM media WHERE id = %s", (id,))

    def select_by_id(self, id):
        self.cursor.execute(
            "SELECT id, filename, file_id, caption, type, sent FROM media WHERE id = %s",
            (id,),
        )
        return self.cursor.fetchone()

    def select_all_by_type(self, media_type):
        self.cursor.execute(
            """
            SELECT id, filename, file_id, caption, sent
            FROM media
            WHERE type = %s
            ORDER BY id DESC
            """,
            (media_type,),
        )
        return self.cursor.fetchall()

    # ---------- Smart queries ----------

    def select_auto_by_type(self, media_type):
        self.cursor.execute(
            """
            SELECT id, file_id, caption FROM media
            WHERE type = %s
              AND sent = (SELECT MIN(sent) FROM media WHERE type = %s)
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (media_type, media_type),
        )
        return self.cursor.fetchone()

    def increment_sent(self, id):
        self.cursor.execute(
            "UPDATE media SET sent = sent + 1 WHERE id = %s",
            (id,),
        )

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

    def get_status_by_type(self, media_type):
        self.cursor.execute(
            "SELECT COUNT(*) FROM media WHERE type = %s AND sent = 0",
            (media_type,),
        )
        unsent = self.cursor.fetchone()[0]

        self.cursor.execute(
            "SELECT COUNT(*) FROM media WHERE type = %s AND sent > 0",
            (media_type,),
        )
        sent = self.cursor.fetchone()[0]

        return {"sent": sent, "unsent": unsent}

def create_table():
    with MediaTableManager() as db :
        db.create_table()

# ---------- AUDIO ----------

def insert_audio(filename, file_id, caption=None):
    with MediaTableManager() as db:
        db.insert(filename, file_id, caption, "audio")


def update_audio(id, file_id, caption):
    with MediaTableManager() as db:
        db.update(id, file_id=file_id, caption=caption)


def get_audio_by_id(id):
    with MediaTableManager() as db:
        return db.select_by_id(id)


def get_all_audios():
    with MediaTableManager() as db:
        return db.select_all_by_type("audio")


def delete_audio(id):
    with MediaTableManager() as db:
        db.delete(id)


# ---------- CLIP ----------

def save_clip(file_id, caption):
    with MediaTableManager() as db:
        db.insert(None, file_id, caption, "clip")


def auto_return_file_id():
    with MediaTableManager() as db:
        return db.select_auto_by_type("clip")


def mark_clip_sent(id):
    with MediaTableManager() as db:
        db.increment_sent(id)


def edit_clip_caption(id, caption):
    with MediaTableManager() as db:
        db.update(id, caption=caption)


def clip_exists(id):
    with MediaTableManager() as db:
        return db.exists(id)


def get_last_clip_id():
    with MediaTableManager() as db:
        return db.get_last_id_by_type("clip")


# ---------- LECTURE ----------

def save_lecture(file_id, caption):
    with MediaTableManager() as db:
        db.insert(None, file_id, caption, "lecture")


def auto_return_lecture():
    with MediaTableManager() as db:
        return db.select_auto_by_type("lecture")


def mark_lecture_sent(id):
    with MediaTableManager() as db:
        db.increment_sent(id)


def get_lecture_status():
    with MediaTableManager() as db:
        return db.get_status_by_type("lecture")
