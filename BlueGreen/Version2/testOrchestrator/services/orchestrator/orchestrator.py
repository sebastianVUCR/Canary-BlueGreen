from flask import Blueprint, jsonify, request, g
from marshmallow import Schema, fields, ValidationError
import sys
import subprocess
from multiprocessing import Process
import pika
import uuid
import logging 
from log_utils import CORRELATION_ID_HEADER

testOrchestrator_bp = Blueprint("testOrchestrator", __name__, url_prefix="/tasks")

RABBITMQ_HOST="localhost"

class TaskSchema(Schema):
    taskID = fields.String(required=False)
    status = fields.String(required=False)
    serverID = fields.String(required=False)
    logs = fields.String(required=False)
    retriggerCommand = fields.String(required=True)


taskSchema = TaskSchema()
logger = logging.getLogger(__name__)

tasks = [
    {"taskID": 1, "status": "ongoing", "serverID": 1, "logs":"", "retriggerCommand":'''python -c "print('hello world')"'''},
    {"taskID": 2, "status": "Cancelled", "serverID": 2, "logs":"Program cancelled", "retriggerCommand":'''python -c "print('hello world')"'''},
    {"taskID": 3, "status": "Pass", "serverID": 3, "logs":"Program finished", "retriggerCommand":'''python -c "print('hello world')"'''},
    {"taskID": 3, "status": "Fail", "serverID": 1, "logs":"Index out of bound", "retriggerCommand":'''python -c "cmd /c echo hola"'''}
]

@testOrchestrator_bp.before_request
def set_correlation_id():
    g.correlation_id = request.headers.get(
        CORRELATION_ID_HEADER, str(uuid.uuid4()))


@testOrchestrator_bp.after_request
def add_correlation_id_to_response(response):
    response.headers[CORRELATION_ID_HEADER] = g.correlation_id
    return response

@testOrchestrator_bp.route("/", methods=["GET"])
def getTasks():
    """
    Get all tasks' information
    ---
    tags:
      - tasks
    responses:
      200:
        description: A list of tasks, secure password and auth is pending.
        schema:
          type: array
          items:
            id: Tasks
            properties:
              taskID:
                type: integer
              status:
                type: string
              serverID:
                type: integer
              logs:
                type: string
              retriggerCommand: string
    """
    logger.info(f"Obteniendo tareas {tasks}")
    return jsonify(tasks), 200

def findTask(taskID):
    # usando for
    for task in tasks:
        if task["taskID"] == taskID:
            return task
    return None

@testOrchestrator_bp.route('/update/<int:taskID>', methods=['PUT'])
def changeStatus(taskID):
    """
    Updates the status of a task
    ---
    tags:
      - tasks
    parameters:
      - name: taskID
        in: path
        type: integer
        required: false
      - name: body
        in: body
        required: false
        schema:
          type: object
          properties:
            status:
              type: string
    responses:
      200:
        description: Task's status updated
      404:
        description: Task not found
    """
    #validation can be improved
    try:
        data = request.get_json()
    except ValidationError as err:
        return jsonify(err.messages), 400
    return executeChangeStatus(taskID, data["status"])

def executeChangeStatus(taskID, newStatus):
    task = findTask(taskID)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    task["status"] = newStatus

    logger.info(f"Informacion modificada en {task}")
    return jsonify(task), 200

@testOrchestrator_bp.route('/tasks', methods=['POST'])
def triggerTask():
    """
    Add a new task
    ---
    tags:
      - tasks
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            serverID:
              type: int
            retriggerCommand:
              type: string
    responses:
      201:
        description: User added
    """
    try:
        data = taskSchema.load(request.get_json())
    except ValidationError as err:
        return jsonify(err.messages), 400

    #For the minimum viable product the server must be selected by the user.
    newTask = {
        "taskID": len(tasks) + 1,
        "status": "ongoing",
        "serverID": data["serverID"],
        "logs": "",
        "retriggerCommand":data["retriggerCommand"]
    }
    tasks.append(newTask)
    async_trigger(newTask)
    logger.info(f"Tarea creada {newTask}")
    return jsonify(newTask), 201

def async_trigger(data):
    execute_command(data["retriggerCommand"])
    executeChangeStatus(data["taskID"],"Passed")
    add_to_queue(data)

def add_to_queue(data):
    # Conectarse a RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters(
          host='rabbitmq'))

    # Crear un canal
    channel = connection.channel()
    channel.queue_declare(queue='tasksQueue')

    # Publicar un mensaje
    channel.basic_publish(exchange='', routing_key='tasksQueue',
                          body=str(data))
    # Cerrar la conexión
    connection.close()

def execute_command(command):
    """
    Executes a command using subprocess.run. If the command fails (returns a non-zero
    exit code), it prints the error to the parent's stderr and exits the parent
    process with the same exit code.

    Args:
        command (list or str): The command and its arguments as a list, or a
                                shell command string. Using a list is generally
                                recommended to avoid shell injection vulnerabilities.
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            print(f"Error executing command: {command}", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)
        else:
            print(result.stdout)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
