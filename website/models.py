import os
import mysql.connector
from mysql.connector import Error
from flask_login import UserMixin


import os
import mysql.connector

def create_connection():
    ca_path = os.path.join(
        os.path.dirname(__file__),
        "ca.pem"
    )

    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ.get("MYSQL_PORT", "17619")),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ.get("MYSQL_DATABASE", "defaultdb"),
        charset="utf8mb4",
        ssl_ca=ca_path,
        ssl_verify_cert=True
    )
class User(UserMixin):
    def __init__(self, user_id, username, email):
        self.id = str(user_id)
        self.username = username
        self.email = email


def create_table():
    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(100) NOT NULL,
                email VARCHAR(250) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                note_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(200) NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
                    ON DELETE CASCADE
            )
        """)

        connection.commit()

    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_user_by_email(email):
    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, user_name, email, password
            FROM users
            WHERE email = %s
        """, (email,))

        row = cursor.fetchone()

        if row:
            return row

        return None

    except Error as error:
        print("Find user error:", error)
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_user_by_id(user_id):
    connection = create_connection()
    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, user_name, email
            FROM users
            WHERE user_id = %s
        """, (user_id,))

        row = cursor.fetchone()

        if row:
            return User(
                user_id=row["user_id"],
                username=row["user_name"],
                email=row["email"]
            )

        return None

    except Error as error:
        print("Find user by ID error:", error)
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()


def create_note(user_id, title, content):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO notes (user_id, title, content)
            VALUES (%s, %s, %s)
        """, (user_id, title, content))

        connection.commit()
        return True

    except Error as error:
        print("Error creating note:", error)
        if connection:
            connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_notes(user_id):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT note_id, title, content, created_at
            FROM notes
            WHERE user_id = %s
            ORDER BY created_at DESC, note_id DESC
        """, (user_id,))
        return cursor.fetchall()

    except Error as error:
        print("Error retrieving notes:", error)
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_note(user_id, note_id):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT note_id, title, content, created_at
            FROM notes
            WHERE user_id = %s AND note_id = %s
        """, (user_id, note_id))
        return cursor.fetchone()

    except Error as error:
        print("Error retrieving note:", error)
        return None

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def update_note(user_id, note_id, title, content):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE notes
            SET title = %s, content = %s
            WHERE user_id = %s AND note_id = %s
        """, (title, content, user_id, note_id))
        connection.commit()
        if cursor.rowcount > 0:
            return True

        cursor.execute("""
            SELECT note_id
            FROM notes
            WHERE user_id = %s AND note_id = %s
        """, (user_id, note_id))
        return cursor.fetchone() is not None

    except Error as error:
        print("Error updating note:", error)
        if connection:
            connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def delete_note(user_id, note_id):
    connection = None
    cursor = None

    try:
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM notes
            WHERE user_id = %s AND note_id = %s
        """, (user_id, note_id))
        connection.commit()
        return cursor.rowcount > 0

    except Error as error:
        print("Error deleting note:", error)
        if connection:
            connection.rollback()
        return False

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
