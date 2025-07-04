from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, ValidationError

users_bp = Blueprint("users", __name__, url_prefix="/users")

class UserSchema(Schema):
    name = fields.String(required=True)
    password = fields.String(required=True)
    roles = fields.List(fields.String(), required=True)

user_schema = UserSchema()

users = [
    {"id": 1, "name": "Admin", "password": "admin", "roles":["admin"]},
    {"id": 2, "name": "Bob", "password": "Bob", "roles":["testExecuter"]},
    {"id": 3, "name": "Ana", "password": "Ana", "roles":["manager", "testExecuter"]}
]


@users_bp.route("/", methods=["GET"])
def get_users():
    """
    Get all users
    ---
    tags:
      - users
    responses:
      200:
        description: A list of users, secure password and auth is pending.
        schema:
          type: array
          items:
            id: User
            properties:
              id:
                type: integer
              name:
                type: string
              password:
                type: confidential
              roles:
                type: list
    """
    return jsonify(users), 200

@users_bp.route('/users', methods=['POST'])
def add_user():
    """
    Add a new user
    ---
    tags:
      - users
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            password:
              type: string
            roles:
              type: List
    responses:
      201:
        description: User added
    """
    try:
        data = user_schema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_user = {
        "id": len(users) + 1,
        "name": data["name"],
        "password": data["password"],
        "roles": data["roles"],
    }
    users.append(new_user)
    return jsonify(new_user), 201

@users_bp.route('/users/changePassword/<int:user_id>', methods=['PUT'])
def update_role(user_id):
    """
    Change a password
    ---
    tags:
      - users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            roles:
              type: List
    responses:
      200:
        description: User updated
      404:
        description: User not found
    """
    user = find_user(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    try:
        data = request.get_json()
    except ValidationError as err:
        return jsonify(err.messages), 400


    
    user["roles"] = data["roles"]

    return jsonify(user), 200

def find_user(user_id):
    # usando for
    for user in users:
        if user["id"] == user_id:
            return user
    return None

@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    Delete a user
    ---
    tags:
      - users
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
    responses:
      204:
        description: User deleted
      404:
        description: User not found
    """
    # si no usamos global, python asume que books es variable local
    global users
    # creamos una nueva lista sin el libro que queremos eliminar
    users = [user for user in users if user["id"] != user_id]
    return "", 204
