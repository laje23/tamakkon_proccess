from models.database_connection import get_connection


class GameResultsTable:
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
            CREATE TABLE IF NOT EXISTS game_results (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                collection_id INTEGER NOT NULL REFERENCES collections(id),
                is_winner SMALLINT NOT NULL CHECK (is_winner IN (0, 1))
            );
            """
        )

    def insert_result(self, user_id, collection_id, is_winner):
        self.cursor.execute(
            """
            INSERT INTO game_results (user_id, collection_id, is_winner)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (user_id, collection_id, is_winner),
        )
        return self.cursor.fetchone()[0]

    def get_results_by_user(self, user_id):
        self.cursor.execute(
            """
            SELECT id, user_id, collection_id, is_winner
            FROM game_results
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (user_id,),
        )
        return self.cursor.fetchall()

    def get_results_by_collection(self, collection_id):
        self.cursor.execute(
            """
            SELECT id, user_id, collection_id, is_winner
            FROM game_results
            WHERE collection_id = %s
            ORDER BY id DESC
            """,
            (collection_id,),
        )
        return self.cursor.fetchall()

    def get_results_by_flag(self, collection_id, flag):
        self.cursor.execute(
            """
            SELECT id, user_id
            FROM game_results
            WHERE collection_id = %s AND is_winner = %s
            ORDER BY id DESC
            """,
            (collection_id, flag),
        )
        return self.cursor.fetchall()

    def delete_result(self, result_id):
        self.cursor.execute(
            "DELETE FROM game_results WHERE id = %s",
            (result_id,),
        )


def create_results_table():
    with GameResultsTable() as db:
        db._create_table()


def add_result(user_id, collection_id, is_winner):
    with GameResultsTable() as db:
        return db.insert_result(user_id, collection_id, is_winner)


def get_user_results(user_id):
    with GameResultsTable() as db:
        return db.get_results_by_user(user_id)


def get_collection_results(collection_id):
    with GameResultsTable() as db:
        return db.get_results_by_collection(collection_id)


def get_collection_winners(collection_id):
    with GameResultsTable() as db:
        return db.get_results_by_flag(collection_id, 1)


def get_collection_losers(collection_id):
    with GameResultsTable() as db:
        return db.get_results_by_flag(collection_id, 0)


def delete_result(result_id):
    with GameResultsTable() as db:
        db.delete_result(result_id)
