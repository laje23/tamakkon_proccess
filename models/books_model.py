from .database_connection import get_connection


class BooksTableManager:
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
            CREATE TABLE IF NOT EXISTS books (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                publisher TEXT,
                excerpt TEXT,
                sent INTEGER DEFAULT 0 CHECK (sent IN (0, 1))
            );
        """
        )

    def insert_book(self, title, author, publisher=None, excerpt=None):
        self.cursor.execute(
            """
            INSERT INTO books (title, author, publisher, excerpt, sent)
            VALUES (%s, %s, %s, %s, 0)
        """,
            (title, author, publisher, excerpt),
        )

    def update_book(self, book_id, title, author, publisher=None, excerpt=None):
        self.cursor.execute(
            """
            UPDATE books
            SET title = %s,
                author = %s,
                publisher = %s,
                excerpt = %s
            WHERE id = %s
        """,
            (title, author, publisher, excerpt, book_id),
        )

    def get_unsent_book(self):
        self.cursor.execute(
            """
            SELECT id, title, author, publisher, excerpt
            FROM books
            WHERE sent = 0
            ORDER BY RANDOM()
            LIMIT 1
        """
        )
        result = self.cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "title": result[1],
                "author": result[2],
                "publisher": result[3],
                "excerpt": result[4],
            }
        return None

    def mark_book_sent(self, book_id):
        self.cursor.execute("UPDATE books SET sent = 1 WHERE id = %s", (book_id,))

    def get_sent_unsent_counts(self):
        self.cursor.execute("SELECT COUNT(*) FROM books WHERE sent = 1")
        sent = self.cursor.fetchone()[0]

        self.cursor.execute("SELECT COUNT(*) FROM books WHERE sent = 0")
        unsent = self.cursor.fetchone()[0]

        return {"sent": sent, "unsent": unsent}

    def book_exists(self, book_id):
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM books WHERE id = %s)", (book_id,)
        )
        return self.cursor.fetchone()[0]


def create_table():
    with BooksTableManager() as db:
        db.create_table()


def save_book(title, author, publisher=None, excerpt=None):
    with BooksTableManager() as db:
        db.insert_book(title, author, publisher, excerpt)


def edit_book(book_id, title, author, publisher=None, excerpt=None):
    with BooksTableManager() as db:
        db.update_book(book_id, title, author, publisher, excerpt)


def get_unsent_book():
    with BooksTableManager() as db:
        return db.get_unsent_book()


def mark_book_sent(book_id):
    with BooksTableManager() as db:
        db.mark_book_sent(book_id)


def get_status():
    with BooksTableManager() as db:
        return db.get_sent_unsent_counts()


def check_book_exists(book_id):
    with BooksTableManager() as db:
        return db.book_exists(book_id)
