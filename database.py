import os
import mysql.connector
from mysql.connector import Error


def connect():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'job_tracker')
    )


def query(sql, params=None):
    connection = connect()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        return rows
    finally:
        cursor.close()
        connection.close()


def execute(sql, params=None):
    connection = connect()
    cursor = connection.cursor()
    try:
        cursor.execute(sql, params or ())
        connection.commit()
        return cursor.lastrowid
    except Error:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def get_options():
    return {
        'companies': query('SELECT company_id, name FROM companies ORDER BY name'),
        'jobs': query('SELECT j.job_id, j.title, c.name AS company_name FROM jobs j JOIN companies c ON j.company_id=c.company_id ORDER BY j.title')
    }
