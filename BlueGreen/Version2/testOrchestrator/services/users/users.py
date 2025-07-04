from flask import Blueprint, jsonify, request, g
from marshmallow import Schema, fields, ValidationError
import uuid
import logging 
from log_utils import CORRELATION_ID_HEADER

users_bp = Blueprint("users", __name__, url_prefix="/users")

class UserSchema(Schema):
    name = fields.String(required=True)
    password = fields.String(required=True)
    roles = fields.List(fields.String(), required=True)

user_schema = UserSchema()
logger = logging.getLogger(__name__)

users = [
    {"id": 1, "name": "Admin", "password": "admin", "roles":["admin"]},
    {"id": 2, "name": "Bob", "password": "Bob", "roles":["testExecuter"]},
    {"id": 3, "name": "Ana", "password": "Ana", "roles":["manager", "testExecuter"]}
]

@users_bp.before_request
def set_correlation_id():
    g.correlation_id = request.headers.get(
        CORRELATION_ID_HEADER, str(uuid.uuid4()))


@users_bp.after_request
def add_correlation_id_to_response(response):
    response.headers[CORRELATION_ID_HEADER] = g.correlation_id
    return response

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
    logger.info(f"Obteniendo usuarios {users}")
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
        logger.info(f"Error al agregar usuario: {err.messages}")
        return jsonify(err.messages), 400

    new_user = {
        "id": len(users) + 1,
        "name": data["name"],
        "password": data["password"],
        "roles": data["roles"],
    }
    users.append(new_user)
    logger.info(f"Usuario agregado: {new_user} en {users}")
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
        logger.info(f"no se encontro usuario: {user_id}")
        return jsonify({"error": "User not found"}), 404
    
    try:
        data = request.get_json()
        logger.info(f"Informacion de usuario cambiada: {user}")
    except ValidationError as err:
        logger.info(f"Error al actualizar: {user_id}")
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
    logger.info(f"Solicitud para borrar usuario {user_id} lista actual de usuarios: {users}")
    return "", 204
