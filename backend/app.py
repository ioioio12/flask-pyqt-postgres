import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from flasgger import Swagger, swag_from

# http://localhost:5000/apidocs для просмотра документации

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

DB_CONFIG = {
    "dbname": "ku",
    "user": "postgres",
    "password": "123",
    "host": "localhost",
    "port": "5432"
}


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


def create_table():
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


create_table()


@app.route("/users", methods=["GET"])
@swag_from({
    'responses': {
        200: {
            'description': 'List of users',
            'examples': {
                'application/json': [{"id": 1, "name": "John Doe"}]
            }
        }
    }
})
def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users")
    users = [{"id": row[0], "name": row[1]} for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(users)


@app.route("/users", methods=["POST"])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'}
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        201: {'description': 'User added successfully'},
        400: {'description': 'Name is required'}
    }
})
def add_user():
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name) VALUES (%s) RETURNING id", (name,))
    user_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": user_id, "message": "User added"}), 201


@app.route("/users/<int:user_id>", methods=["DELETE"])
@swag_from({
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        }
    ],
    'responses': {
        200: {'description': 'User deleted'}
    }
})
def delete_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User deleted"}), 200


@app.route("/users/<int:user_id>", methods=["PUT"])
@swag_from({
    'parameters': [
        {
            'name': 'user_id',
            'in': 'path',
            'type': 'integer',
            'required': True
        },
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'}
                },
                'required': ['name']
            }
        }
    ],
    'responses': {
        200: {'description': 'User updated'},
        400: {'description': 'Name is required'}
    }
})
def update_user(user_id):
    data = request.json
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = %s WHERE id = %s", (name, user_id))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "User updated"}), 200


if __name__ == "__main__":
    app.run(debug=True)


# http://localhost:5000/apidocs
