# models/lecture_model.py

from models.database_connection import get_connection

class LectureTableManager:
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
            CREATE TABLE IF NOT EXISTS lectures (
                id SERIAL PRIMARY KEY,
                media_id INT NOT NULL REFERENCES media(id) ON DELETE CASCADE,
                caption TEXT,
                sent BOOLEAN DEFAULT FALSE
            );
            """
        )

    # ---------- CRUD ----------

    def insert(self, media_id, caption=None, sent=False):
        self.cursor.execute(
            """
            INSERT INTO lectures (media_id, caption, sent)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (media_id, caption, sent),
        )
        lecture_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return lecture_id

    def update_caption(self, lecture_id, new_caption):
        self.cursor.execute(
            "UPDATE lectures SET caption = %s WHERE id = %s",
            (new_caption, lecture_id),
        )

    def mark_as_sent(self, lecture_id):
        """علامت زدن یک سخنرانی به عنوان ارسال شده"""
        self.cursor.execute(
            "UPDATE lectures SET sent = TRUE WHERE id = %s",
            (lecture_id,),
        )

    def delete(self, lecture_id):
        self.cursor.execute("DELETE FROM lectures WHERE id = %s", (lecture_id,))

    def get_by_id(self, lecture_id):
        self.cursor.execute(
            """
            SELECT l.id, l.caption, l.sent, m.file_id
            FROM lectures l
            JOIN media m ON l.media_id = m.id
            WHERE l.id = %s
            """,
            (lecture_id,),
        )
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute(
            """
            SELECT l.id, l.caption, l.sent, m.file_id
            FROM lectures l
            JOIN media m ON l.media_id = m.id
            ORDER BY l.id DESC
            """
        )
        return self.cursor.fetchall()

    def get_one_unsent(self):
        """یک رکورد ارسال نشده را برمی‌گرداند"""
        self.cursor.execute(
            """
            SELECT l.id, l.caption, l.sent, m.file_id
            FROM lectures l
            JOIN media m ON l.media_id = m.id
            WHERE l.sent = FALSE
            ORDER BY l.id ASC
            LIMIT 1
            """
        )
        return self.cursor.fetchone()



def create_table():
    with LectureTableManager()as db :
        db.create_table()