# models/clip_model.py

from models.database_connection import get_connection

class ClipTableManager:
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
            CREATE TABLE IF NOT EXISTS clips (
                id SERIAL PRIMARY KEY,
                media_id INT NOT NULL REFERENCES media(id) ON DELETE CASCADE,
                caption TEXT ,
                sent BOOLEAN DEFAULT FALSE
            );
            """
        )

    # ---------- CRUD ----------

    def insert(self, media_id, caption=None):
        self.cursor.execute(
            """
            INSERT INTO clips (media_id, caption)
            VALUES (%s, %s)
            RETURNING id
            """,
            (media_id, caption),
        )
        clip_id = self.cursor.fetchone()[0]
        self.conn.commit()
        return clip_id

    def update_caption(self, clip_id, new_caption):
        self.cursor.execute(
            "UPDATE clips SET caption = %s WHERE id = %s",
            (new_caption, clip_id),
        )

    def delete(self, clip_id):
        self.cursor.execute("DELETE FROM clips WHERE id = %s", (clip_id,))

    def get_by_id(self, clip_id):
        self.cursor.execute(
            """
            SELECT c.id, c.caption, c.sent m.file_id
            FROM clips c
            JOIN media m ON c.media_id = m.id
            WHERE c.id = %s
            """,
            (clip_id,),
        )
        return self.cursor.fetchone()

    def get_all(self):
        self.cursor.execute(
            """
            SELECT c.id, c.caption, c.sent m.file_id
            FROM clips c
            JOIN media m ON c.media_id = m.id
            ORDER BY c.id DESC
            """
        )
        return self.cursor.fetchall()

    def get_own_unsent(self):
        self.cursor.execute(
            """
            SELECT c.id, c.caption, c.sent ,m.file_id
            FROM clips c
            JOIN media m ON c.media_id = m.id
            WHERE c.sent = FALSE LIMIT 1
            """
        )
        return self.cursor.fetchone()
    
    def mark_as_sent(self, clip_id):
        """علامت زدن یک کلیپ به عنوان ارسال شده"""
        self.cursor.execute(
            "UPDATE clips SET sent = TRUE WHERE id = %s",
            (clip_id,),
        )
        
        

def create_table():
    with ClipTableManager()as db :
        db.create_table()