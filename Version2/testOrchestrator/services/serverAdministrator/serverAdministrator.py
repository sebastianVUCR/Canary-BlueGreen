from flask import Blueprint, jsonify, request, g
from marshmallow import Schema, fields, ValidationError
import uuid
import logging 
from log_utils import CORRELATION_ID_HEADER

serverAdministrator_bp = Blueprint("servers", __name__, url_prefix="/servers")

class ServerSchema(Schema):
    name = fields.String(required=True)
    ip = fields.String(required=True)
    info = fields.List(fields.String(), required=True)

serverSchema = ServerSchema()
logger = logging.getLogger(__name__)

#Can be normalized on a data base.
servers = [
    {"id": 1, "name": "Server1", "ip": "192.000.000", "info":["Linux"]},
    {"id": 2, "name": "Server2", "ip": "192.000.001", "info":["8 cores"]},
    {"id": 3, "name": "Server3", "ip": "192.000.002", "info":["Desktop", "Windows"]}
]

@serverAdministrator_bp.before_request
def set_correlation_id():
    g.correlation_id = request.headers.get(
        CORRELATION_ID_HEADER, str(uuid.uuid4()))


@serverAdministrator_bp.after_request
def add_correlation_id_to_response(response):
    response.headers[CORRELATION_ID_HEADER] = g.correlation_id
    return response

@serverAdministrator_bp.route("/", methods=["GET"])
def getServers():
    """
    Get all servers
    ---
    tags:
      - servers
    responses:
      200:
        description: A list of servers.
        schema:
          type: array
          items:
            id: Server
            properties:
              id:
                type: integer
              name:
                type: string
              ip:
                type: confidential
              info:
                type: list
    """
    logger.info(f"Obteniendo lista de servidores {servers}")
    return jsonify(servers), 200

@serverAdministrator_bp.route('/servers', methods=['POST'])
def addServer():
    """
    Add a new server
    ---
    tags:
      - servers
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            ip:
              type: string
            info:
              type: List
    responses:
      201:
        description: Server added
    """
    try:
        data = serverSchema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    newServer = {
        "id": len(servers) + 1,
        "name": data["name"],
        "ip": data["ip"],
        "info": data["info"],
    }
    servers.append(newServer)
    logger.info(f"Servidor agregado {newServer}")
    return jsonify(newServer), 201

@serverAdministrator_bp.route('/servers/changeip/<int:serverId>', methods=['PUT'])
def updateInfo(serverId):
    """
    Change a ip
    ---
    tags:
      - servers
    parameters:
      - name: serverId
        in: path
        type: integer
        required: true
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            info:
              type: List
            name:
              type: string
    responses:
      200:
        description: Server updated
      404:
        description: Server info not found
    """
    server = findServer(serverId)
    if not server:
        return jsonify({"error": "Server not found"}), 404
    
    try:
        data = request.get_json()
    except ValidationError as err:
        return jsonify(err.messages), 400


    
    server["info"] = data["info"]
    server["name"] = data["name"]

    logger.info(f"Informacion actualizada {server}")

    return jsonify(server), 200

def findServer(serverId):
    # usando for
    for server in servers:
        if server["id"] == serverId:
            return server
    return None

@serverAdministrator_bp.route('/servers/<int:serverId>', methods=['DELETE'])
def deleteServer(serverId):
    """
    Delete a book
    ---
    tags:
      - servers
    parameters:
      - name: serverId
        in: path
        type: integer
        required: true
    responses:
      204:
        description: Server deleted
      404:
        description: Server not found
    """
    # si no usamos global, python asume que books es variable local
    global servers
    # creamos una nueva lista sin el libro que queremos eliminar
    servers = [server for server in servers if server["id"] != serverId]
    logger.info(f"Servidor borrado, lista actual:{servers}")
    return "", 204
