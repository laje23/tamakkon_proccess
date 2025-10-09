from models.database_connection import get_connection


class LecturesTable:
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
            CREATE TABLE IF NOT EXISTS lectures (
                id SERIAL PRIMARY KEY,
                file_id TEXT NOT NULL,
                caption TEXT,
                sent INTEGER DEFAULT 0 CHECK (sent >= 0)
            );
            """
        )

    def insert_row(self, file_id, caption):
        self.cursor.execute("SELECT MIN(sent) FROM lectures")
        min_sent = self.cursor.fetchone()[0]
        if min_sent is None:
            min_sent = 0

        self.cursor.execute(
            "INSERT INTO lectures (file_id, caption, sent) VALUES (%s, %s, %s)",
            (file_id, caption, min_sent),
        )

    def select_auto_file_id(self):
        self.cursor.execute(
            """
            SELECT id, file_id, caption FROM lectures
            WHERE sent = (SELECT MIN(sent) FROM lectures)
            ORDER BY RANDOM()
            LIMIT 1
            """
        )
        result = self.cursor.fetchone()
        return result if result else None

    def increment_sent(self, id):
        self.cursor.execute(
            "UPDATE lectures SET sent = sent + 1 WHERE id = %s",
            (id,),
        )

    def get_sent_unsent_counts(self):
        self.cursor.execute("SELECT COUNT(*) FROM lectures WHERE sent = 0")
        unsent = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM lectures WHERE sent > 0")
        sent = self.cursor.fetchone()[0]

        return {"sent": sent, "unsent": unsent}


def create_table():
    with LecturesTable() as db:
        db._create_table()


def save_lecture(file_id, caption):
    with LecturesTable() as db:
        db.insert_row(file_id, caption)


def mark_lecture_sent(id):
    with LecturesTable() as db:
        db.increment_sent(id)


def auto_return_lecture():
    with LecturesTable() as db:
        return db.select_auto_file_id()


def get_status():
    with LecturesTable() as db:
        return db.get_sent_unsent_counts()
