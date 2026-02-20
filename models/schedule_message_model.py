# models/scheduled_message_table_manager.py

from models.database_connection import get_connection
from datetime import datetime


class ScheduledMessageTableManager:
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
            CREATE TABLE IF NOT EXISTS scheduled_messages (
                id SERIAL PRIMARY KEY,
                media_id INTEGER REFERENCES media(id) ON DELETE SET NULL,
                content TEXT,
                send_at TIMESTAMP WITH TIME ZONE NOT NULL,
                status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'failed')),
                retry_count INTEGER DEFAULT 0 CHECK (retry_count >= 0),
                CHECK (media_id IS NOT NULL OR content IS NOT NULL)
            );
            """
        )

    # ---------- Generic CRUD ----------
    def insert(self, send_at, media_id=None, content=None):
        self.cursor.execute(
            """
            INSERT INTO scheduled_messages (send_at, media_id, content)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (send_at, media_id, content),
        )
        return self.cursor.fetchone()[0]

    def update_status(self, id, status):
        self.cursor.execute(
            "UPDATE scheduled_messages SET status = %s WHERE id = %s",
            (status, id),
        )

    def increment_retry(self, id):
        self.cursor.execute(
            "UPDATE scheduled_messages SET retry_count = retry_count + 1 WHERE id = %s",
            (id,),
        )

    def delete(self, id):
        # گرفتن media_id با JOIN
        self.cursor.execute(
            """
            SELECT m.id
            FROM scheduled_messages sm
            LEFT JOIN media m ON sm.media_id = m.id
            WHERE sm.id = %s
            """,
            (id,),
        )
        row = self.cursor.fetchone()

        if not row:
            return False

        media_id = row[0]

        # حذف پیام
        self.cursor.execute(
            "DELETE FROM scheduled_messages WHERE id = %s",
            (id,),
        )

        # اگر مدیا داشت → فقط اگر جای دیگه استفاده نشده باشد حذف شود
        if media_id:
            self.cursor.execute(
                """
                DELETE FROM media
                WHERE id = %s
                AND NOT EXISTS (
                    SELECT 1 FROM scheduled_messages
                    WHERE media_id = %s
                )
                """,
                (media_id, media_id),
            )

        return True

    def select_by_id(self, id):
        self.cursor.execute(
            """
            SELECT id, media_id, content, send_at, status, retry_count
            FROM scheduled_messages
            WHERE id = %s
            """,
            (id,),
        )
        return self.cursor.fetchone()

    def select_pending(self, limit=10):
        self.cursor.execute(
            """
            SELECT
                sm.id,
                sm.media_id,
                sm.content,
                sm.send_at,
                m.file_id,
                m.type
            FROM scheduled_messages sm
            LEFT JOIN media m ON sm.media_id = m.id
            WHERE sm.status = 'pending'
            AND sm.send_at <= NOW()
            ORDER BY sm.send_at ASC
            LIMIT %s
            """,
            (limit,),
        )
        return self.cursor.fetchall()

    def select_all(self):
        self.cursor.execute(
            """
            SELECT
                sm.id,
                sm.media_id,
                sm.content,
                sm.send_at,
                sm.status,
                sm.retry_count,
                m.file_id,
                m.type AS media_type,
                m.caption AS media_caption
            FROM scheduled_messages sm
            LEFT JOIN media m ON sm.media_id = m.id
            ORDER BY sm.send_at ASC
            """
        )
        return self.cursor.fetchall()

    def select_failed(self, limit=5, max_retry=3):
        self.cursor.execute(
            """
            SELECT sm.id, sm.media_id, sm.send_at, m.file_id, m.type, sm.retry_count
            FROM scheduled_messages sm
            LEFT JOIN media m ON sm.media_id = m.id
            WHERE sm.status = 'failed'
            AND sm.retry_count < %s
            ORDER BY sm.send_at ASC
            LIMIT %s
            """,
            (max_retry, limit),
        )
        return self.cursor.fetchall()


# ---------- Context Wrapper ----------
def create_table():
    with ScheduledMessageTableManager() as db:
        db.create_table()


# ---------- CRUD Wrapper Functions ----------
def insert_message(send_at, media_file_id=None, media_type=None, content=None):
    media_id = None

    if media_file_id and media_type:
        from models.media_model import MediaTableManager

        with MediaTableManager() as media_db:
            media_id = media_db.insert(
                file_id=media_file_id,
                media_type=media_type,
                caption="",
                filename="",
            )

    with ScheduledMessageTableManager() as db:
        return db.insert(send_at, media_id, content)


def update_message_status(id, status):
    with ScheduledMessageTableManager() as db:
        db.update_status(id, status)


def increment_message_retry(id):
    with ScheduledMessageTableManager() as db:
        db.increment_retry(id)


def delete_message(id):
    with ScheduledMessageTableManager() as db:
        db.delete(id)


def get_message_by_id(id):
    with ScheduledMessageTableManager() as db:
        return db.select_by_id(id)


def get_pending_messages(limit=10):
    with ScheduledMessageTableManager() as db:
        return db.select_pending(limit)


def get_all_messages():
    with ScheduledMessageTableManager() as db:
        return db.select_all()


def get_retry_faild_messages(limit=5, max_retry=3):
    with ScheduledMessageTableManager() as db:
        return db.select_failed(limit, max_retry)
