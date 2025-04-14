# backend/app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.database import create_table, get_all_users, add_user

app = Flask(__name__)
CORS(app)

# Инициализируем таблицу при запуске сервера
create_table()

@app.route("/users", methods=["GET"])
def get_users():
    """Получаем всех пользователей."""
    users = get_all_users()
    return jsonify(users)

@app.route("/users", methods=["POST"])
def add_user_route():
    """Добавляем пользователя."""
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    user_id = add_user(name)
    return jsonify({"id": user_id, "message": "User added"}), 201

if __name__ == "__main__":
    app.run(debug=True)
