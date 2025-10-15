# db.py
import psycopg2
import os
from dotenv import load_dotenv


def get_connection():
    try:
        return psycopg2.connect(
            dbname=os.getenv("PGDATABASE"),
            user=os.getenv("POSTGRES"),
            password=os.getenv("PGPASSWORD", 0),
            host=os.getenv("PGHOST"),
            port=5432,
        )
    except psycopg2.Error as e:
        print("connection to db fail : ", e)
        return None
