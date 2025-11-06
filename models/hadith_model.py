from models.database_connection import get_connection


class HadithTableManager:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS hadith (
                id SERIAL PRIMARY KEY,
                message_id INTEGER DEFAULT NULL,
                content TEXT DEFAULT NULL,
                sent INTEGER DEFAULT 0 CHECK (sent IN (0,1))
            );
            """
        )

    def insert_row(self, message_id, content):
        # گرفتن کمترین مقدار sent از جدول
        self.cursor.execute("SELECT MIN(sent) FROM hadith")
        min_sent = self.cursor.fetchone()[0]

        # اگر جدول خالی بود، مقدار اولیه رو صفر بذار
        if min_sent is None:
            min_sent = 0

        # درج رکورد جدید با مقدار sent برابر با کمترین مقدار موجود
        self.cursor.execute(
            "INSERT INTO hadith (message_id, content, sent) VALUES (%s, %s, %s)",
            (message_id, content, min_sent),
        )

    def update_content(self, message_id, new_content):
        self.cursor.execute(
            "UPDATE hadith SET content = %s WHERE message_id = %s",
            (new_content, message_id),
        )

    def update_sent_to_1(self, id, content):
        self.cursor.execute(
            "UPDATE hadith SET sent = 1 WHERE id = %s OR content = %s",
            (id, content),
        )

    def select_unsent(self):
        self.cursor.execute(
            """
            SELECT content, id FROM hadith
            WHERE sent = (
                SELECT MIN(sent) FROM hadith
            )
            ORDER BY RANDOM()
            LIMIT 1
            """
        )
        return self.cursor.fetchone()

    # تابع آمار تعداد ارسال شده و ارسال نشده
    def get_status_counts(self):
        self.cursor.execute("SELECT COUNT(*) FROM hadith WHERE sent = 0")
        unsent_count = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM hadith WHERE sent = 1")
        sent_count = self.cursor.fetchone()[0]

        return {"sent": sent_count, "unsent": unsent_count}


# 🔹 توابع بیرون کلاس


def create_table():
    with HadithTableManager() as db:
        db.create_table()


def save_id_and_content(message_id, content):
    with HadithTableManager() as db:
        db.insert_row(message_id, content)


def edit_content(message_id, new_content):
    with HadithTableManager() as db:
        db.update_content(message_id, new_content)


def return_auto_content():
    with HadithTableManager() as db:
        return db.select_unsent()


def mark_sent(id=0, content=""):
    with HadithTableManager() as db:
        db.update_sent_to_1(id, content)


def get_status():
    with HadithTableManager() as db:
        return db.get_status_counts()
