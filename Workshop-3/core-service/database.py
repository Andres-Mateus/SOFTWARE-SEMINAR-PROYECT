"""
The script funcion is connect the PostgreSQL DB with the core-service using pyscopg2
"""

import psycopg2
from psycopg2 import sql


def try_connection():
    host = "localhost"
    user = "admon"
    password = "admon"
    database = "parking"
    try:
        conecction = psycopg2.connect(
            host="localhost", database=database, user=user, password=password
        )
        cursor = conecction.cursor()
        cursor.execute("SELECT version()")
        row = cursor.fetchone()
        return f"Connected succesfully: {row}"
    except Exception as ex:
        return f"Connection Fail: {ex}"


def get_connection():
    host = "localhost"
    user = "admon"
    password = "admon"
    database = "parking"
    return psycopg2.connect(
        host="localhost", database=database, user=user, password=password
    )


def run_query(query, params=None, fetch=False):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    if fetch:
        result = cur.fetchall()
    else:
        result = None
    conn.commit()
    cur.close()
    conn.close()
    return result
