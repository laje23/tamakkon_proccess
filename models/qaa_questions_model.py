from models.database_connection import get_connection


class QuestionsTable:
    def __init__(self):
        self.conn = get_connection()
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.conn.commit()
        else:
            self.conn.rollback()
        self.cursor.close()
        self.conn.close()

    def _create_table(self):
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                collection_id INTEGER NOT NULL REFERENCES collections(id),
                question_index INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                option1 TEXT NOT NULL,
                option2 TEXT NOT NULL,
                option3 TEXT NOT NULL,
                correct TEXT NOT NULL
            );
            """
        )

    # ---------------- GETTERS ---------------- #

    def get_next_index(self, collection_id):
        self.cursor.execute(
            "SELECT COALESCE(MAX(question_index), 0) + 1 FROM questions WHERE collection_id = %s",
            (collection_id,),
        )
        return self.cursor.fetchone()[0]

    def get_question_by_index(self, collection_id, question_index):
        self.cursor.execute(
            """
            SELECT id, collection_id, question_index, question_text,
                option1, option2, option3, correct
            FROM questions
            WHERE collection_id = %s AND question_index = %s
            LIMIT 1
            """,
            (collection_id, question_index),
        )
        return self.cursor.fetchone()

    def get_question_by_collection_id(self, collection_id):
        self.cursor.execute(
            """
            SELECT id, collection_id, question_index, question_text,
                option1, option2, option3, correct
            FROM questions
            WHERE collection_id = %s
            """,
            (collection_id,),
        )
        return self.cursor.fetchall()

    def get_question_by_id(self, question_id):
        self.cursor.execute(
            """
            SELECT id, collection_id, question_index, question_text,
                option1, option2, option3, correct
            FROM questions
            WHERE id = %s
            LIMIT 1
            """,
            (question_id,),
        )
        return self.cursor.fetchone()

    def get_question_count(self, collection_id):
        self.cursor.execute(
            "SELECT COUNT(*) FROM questions WHERE collection_id = %s", (collection_id,)
        )
        return self.cursor.fetchone()[0]

    def get_all_questions(self, collection_id):
        self.cursor.execute(
            """
            SELECT id, question_index, question_text, option1, option2, option3, correct
            FROM questions
            WHERE collection_id = %s
            ORDER BY question_index
            """,
            (collection_id,),
        )
        return self.cursor.fetchall()

    # ---------------- INSERT ---------------- #

    def insert_row(
        self, collection_id, question_text, option1, option2, option3, correct
    ):
        q_index = self.get_next_index(collection_id)

        self.cursor.execute(
            """
            INSERT INTO questions (
                collection_id ,question_index, question_text,
                option1, option2, option3, correct
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (collection_id, q_index, question_text, option1, option2, option3, correct),
        )

        return self.cursor.fetchone()[0]

    # ---------------- UPDATE FUNCTIONS (EDIT PARTS) ---------------- #

    def update_question_text(self, question_id, new_text):
        self.cursor.execute(
            "UPDATE questions SET question_text = %s WHERE id = %s",
            (new_text, question_id),
        )

    def update_option1(self, question_id, new_text):
        self.cursor.execute(
            "UPDATE questions SET option1 = %s WHERE id = %s", (new_text, question_id)
        )

    def update_option2(self, question_id, new_text):
        self.cursor.execute(
            "UPDATE questions SET option2 = %s WHERE id = %s", (new_text, question_id)
        )

    def update_option3(self, question_id, new_text):
        self.cursor.execute(
            "UPDATE questions SET option3 = %s WHERE id = %s", (new_text, question_id)
        )

    def update_correct(self, question_id, new_text):
        self.cursor.execute(
            "UPDATE questions SET correct = %s WHERE id = %s", (new_text, question_id)
        )

    def update_collection(self, question_id, new_collection_id):
        self.cursor.execute(
            "UPDATE questions SET collection_id = %s WHERE id = %s",
            (new_collection_id, question_id),
        )

    def update_index(self, question_id, new_index):
        self.cursor.execute(
            "UPDATE questions SET question_index = %s WHERE id = %s",
            (new_index, question_id),
        )


# ------------------ خارج از کلاس ------------------ #


def create_questions_table():
    with QuestionsTable() as db:
        db._create_table()


def add_question(collection_id, question_text, option1, option2, option3, correct):
    with QuestionsTable() as db:
        return db.insert_row(
            collection_id, question_text, option1, option2, option3, correct
        )


def get_question(collection_id, question_index):
    with QuestionsTable() as db:
        return db.get_question_by_index(collection_id, question_index)


def get_all_question_by_collection_id(collection_id):
    with QuestionsTable() as db:
        return db.get_question_by_collection_id(collection_id)


def get_question_by_id(question_id):
    with QuestionsTable() as db:
        return db.get_question_by_id(question_id)


def get_all_questions(collection_id):
    with QuestionsTable() as db:
        return db.get_all_questions(collection_id)


def get_question_count(collection_id):
    with QuestionsTable() as db:
        return db.get_question_count(collection_id)


# ---- update wrappers ---- #


def update_question_text(question_id, text):
    with QuestionsTable() as db:
        db.update_question_text(question_id, text)


def update_option1(question_id, text):
    with QuestionsTable() as db:
        db.update_option1(question_id, text)


def update_option2(question_id, text):
    with QuestionsTable() as db:
        db.update_option2(question_id, text)


def update_option3(question_id, text):
    with QuestionsTable() as db:
        db.update_option3(question_id, text)


def update_correct(question_id, text):
    with QuestionsTable() as db:
        db.update_correct(question_id, text)


def update_question_collection(question_id, new_collection_id):
    with QuestionsTable() as db:
        db.update_collection(question_id, new_collection_id)


def update_question_index(question_id, new_index):
    with QuestionsTable() as db:
        db.update_index(question_id, new_index)
