import unittest
from backend.app import app, get_db_connection


class FlaskAppTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Создаем тестовую базу данных, если она еще не существует."""
        cls.conn = get_db_connection()
        cls.cur = cls.conn.cursor()
        cls.cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL
            )
        """)
        cls.conn.commit()

    def setUp(self):
        """Метод для очистки таблицы users перед каждым тестом."""
        self.cur.execute("DELETE FROM users")
        self.conn.commit()

    def tearDown(self):
        """Метод для очистки после каждого теста."""
        self.cur.execute("DELETE FROM users")
        self.conn.commit()

    @classmethod
    def tearDownClass(cls):
        """Закрываем соединение с базой данных после всех тестов."""
        cls.cur.close()
        cls.conn.close()

    def test_get_users(self):
        """Тестируем получение списка пользователей."""
        with app.test_client() as client:
            # Проверим, что изначально список пользователей пуст.
            response = client.get('/users')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [])

            # Добавим пользователя и снова проверим.
            self.cur.execute("INSERT INTO users (name) VALUES ('John')")
            self.conn.commit()

            response = client.get('/users')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, [{"id": 1, "name": "John"}])

    def test_add_user(self):
        """Тестируем добавление пользователя."""
        with app.test_client() as client:
            # Попробуем добавить пользователя с валидными данными.
            response = client.post('/users', json={"name": "Alice"})
            self.assertEqual(response.status_code, 201)
            self.assertIn('id', response.json)
            self.assertEqual(response.json['message'], 'User added')

            # Проверим, что пользователь добавился в базу данных.
            self.cur.execute("SELECT name FROM users WHERE id = %s", (response.json['id'],))
            user = self.cur.fetchone()
            self.assertEqual(user[0], 'Alice')

    def test_add_user_without_name(self):
        """Тестируем добавление пользователя без указания имени."""
        with app.test_client() as client:
            response = client.post('/users', json={})
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json, {"error": "Name is required"})


if __name__ == "__main__":
    unittest.main()
