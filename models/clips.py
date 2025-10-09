from models.database_connection import get_connection


class ClipsTable:
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
            CREATE TABLE IF NOT EXISTS clips (
                id SERIAL PRIMARY KEY,
                file_id TEXT NOT NULL,
                caption TEXT,
                sent INTEGER DEFAULT 0 CHECK (sent >= 0)
            );
            """
        )

    def insert_row(self, file_id, caption):
        self.cursor.execute("SELECT MIN(sent) FROM clips")
        min_sent = self.cursor.fetchone()[0]
        if min_sent is None:
            min_sent = 0

        self.cursor.execute(
            "INSERT INTO clips (file_id, caption, sent) VALUES (%s, %s, %s)",
            (file_id, caption, min_sent),
        )

    def edit_caption(self, clip_id: int, new_caption: str):
        self.cursor.execute(
            "UPDATE clips SET caption = %s WHERE id = %s",
            (new_caption, clip_id),
        )

    def select_auto_file_id(self):
        self.cursor.execute(
            """
            SELECT id, file_id, caption FROM clips
            WHERE sent = (SELECT MIN(sent) FROM clips)
            ORDER BY RANDOM()
            LIMIT 1
            """
        )
        result = self.cursor.fetchone()
        return result if result else None

    def increment_sent(self, clip_id):
        self.cursor.execute(
            "UPDATE clips SET sent = sent + 1 WHERE id = %s",
            (clip_id,),
        )

    def get_sent_unsent_counts(self):
        self.cursor.execute("SELECT COUNT(*) FROM clips WHERE sent = 0")
        unsent_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM clips WHERE sent > 0")
        sent_count = self.cursor.fetchone()[0]

        return {"sent": sent_count, "unsent": unsent_count}

    def _is_clip_sent(self, clip_id: int) -> bool:
        self.cursor.execute("SELECT sent FROM clips WHERE id = %s", (clip_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0] > 0
        return False

    def clip_exists(self, clip_id: int) -> bool:
        self.cursor.execute("SELECT 1 FROM clips WHERE id = %s", (clip_id,))
        return self.cursor.fetchone() is not None

    def get_last_clip_id(self) -> int | None:
        self.cursor.execute("SELECT MAX(id) FROM clips")
        result = self.cursor.fetchone()
        return result[0] if result and result[0] is not None else None


def create_table():
    with ClipsTable() as db:
        db._create_table()


def save_clip(file_id, caption):
    with ClipsTable() as db:
        db.insert_row(file_id, caption)


def mark_clip_sent(id):
    with ClipsTable() as db:
        db.increment_sent(id)


def auto_return_file_id():
    with ClipsTable() as db:
        return db.select_auto_file_id()


def get_status():
    with ClipsTable() as db:
        return db.get_sent_unsent_counts()


def check_clip_exists(clip_id: int) -> bool:
    with ClipsTable() as db:
        return db.clip_exists(clip_id)


def get_last_clip_id() -> int | None:
    with ClipsTable() as db:
        return db.get_last_clip_id()


def edit_clip_caption(clip_id: int, new_caption: str):
    with ClipsTable() as db:
        db.edit_caption(clip_id, new_caption)


def is_clip_sent(clip_id: int) -> bool:
    with ClipsTable() as db:
        return db._is_clip_sent(clip_id)
