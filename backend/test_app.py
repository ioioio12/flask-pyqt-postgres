import unittest
import json
from app import app, get_db_connection

class FlaskServerTestCase(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.conn = get_db_connection()
        self.cur = self.conn.cursor()
        # Очистим таблицу перед каждым тестом
        self.cur.execute("DELETE FROM users")
        self.conn.commit()

    def tearDown(self):
        self.cur.close()
        self.conn.close()

    def test_add_user(self):
        response = self.client.post("/users", json={"name": "Test User"})
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("id", data)
        self.assertEqual(data["message"], "User added")

    def test_get_users(self):
        # Добавим одного пользователя сначала
        self.client.post("/users", json={"name": "User One"})
        response = self.client.get("/users")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "User One")

    def test_update_user(self):
        # Добавим пользователя
        response = self.client.post("/users", json={"name": "Old Name"})
        user_id = json.loads(response.data)["id"]

        # Обновим имя
        response = self.client.put(f"/users/{user_id}", json={"name": "New Name"})
        self.assertEqual(response.status_code, 200)

        # Проверим имя
        response = self.client.get("/users")
        users = json.loads(response.data)
        self.assertEqual(users[0]["name"], "New Name")

    def test_delete_user(self):
        # Добавим пользователя
        response = self.client.post("/users", json={"name": "User To Delete"})
        user_id = json.loads(response.data)["id"]

        # Удалим его
        response = self.client.delete(f"/users/{user_id}")
        self.assertEqual(response.status_code, 200)

        # Убедимся, что его больше нет
        response = self.client.get("/users")
        users = json.loads(response.data)
        self.assertEqual(len(users), 0)

    def test_add_user_without_name(self):
        response = self.client.post("/users", json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

    def test_update_user_without_name(self):
        response = self.client.post("/users", json={"name": "Temp"})
        user_id = json.loads(response.data)["id"]
        response = self.client.put(f"/users/{user_id}", json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn("error", data)

if __name__ == "__main__":
    unittest.main()
