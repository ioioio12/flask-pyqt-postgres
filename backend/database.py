
import psycopg2
from backend.config import DB_CONFIG  # Загружаем параметры из конфигурации


def get_db_connection():
    """Создаем и возвращаем подключение к базе данных."""
    return psycopg2.connect(**DB_CONFIG)


def create_table():
    """Создаем таблицу, если она не существует."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_all_users():
    """Получаем всех пользователей из базы данных."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users")
    users = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return users


def add_user(name):
    """Добавляем пользователя в базу данных."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING id", (name,))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return user_id
