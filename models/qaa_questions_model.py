from models.database_connection import get_connection


class QuestionsTable:
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

    def get_next_index(self, collection_id):
        self.cursor.execute(
            "SELECT COALESCE(MAX(question_index), 0) + 1 FROM questions WHERE collection_id = %s",
            (collection_id,),
        )
        return self.cursor.fetchone()[0]

    def insert_row(
        self, collection_id, question_text, option1, option2, option3, correct
    ):
        q_index = self.get_next_index(collection_id)

        self.cursor.execute(
            """
            INSERT INTO questions (
                collection_id, question_index, question_text,
                option1, option2, option3, correct
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (collection_id, q_index, question_text, option1, option2, option3, correct),
        )

        return q_index

    def delete_question(self, question_id):
        self.cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))


def create_questions_table():
    with QuestionsTable() as db:
        db._create_table()


def add_question(collection_id, question_text, option1, option2, option3, correct):
    with QuestionsTable() as db:
        return db.insert_row(
            collection_id, question_text, option1, option2, option3, correct
        )


def delete_question(question_id):
    with QuestionsTable() as db:
        db.delete_question(question_id)
