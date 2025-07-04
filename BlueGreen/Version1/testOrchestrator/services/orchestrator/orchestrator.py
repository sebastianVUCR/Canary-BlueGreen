from flask import Blueprint, jsonify, request
from marshmallow import Schema, fields, ValidationError

testOrchestrator_bp = Blueprint("testOrchestrator", __name__, url_prefix="/tasks")

class UserSchema(Schema):
    name = fields.String(required=True)
    password = fields.String(required=True)
    roles = fields.List(fields.String(), required=True)

user_schema = UserSchema()

tasks = [
    {"taskID": 1, "status": "ongoing", "serverID": 1, "logs":"", "retriggerCommand":"python -c 'print (hello world)'"},
    {"taskID": 2, "status": "Cancelled", "serverID": 2, "logs":"Program cancelled", "retriggerCommand":"python -c 'print (hello world)'"},
    {"taskID": 3, "status": "Pass", "serverID": 3, "logs":"Program finished", "retriggerCommand":"python -c 'print (hello world)'"},
    {"taskID": 3, "status": "Fail", "serverID": 1, "logs":"Index out of bound", "retriggerCommand":"python -c 'print (hello world)'"}
]


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
        required: true
      - name: body
        in: body
        required: true
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
    task = findTask(taskID)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    #validation can be improved
    try:
        data = request.get_json()
    except ValidationError as err:
        return jsonify(err.messages), 400

    
    task["status"] = data["status"]

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
        data = user_schema.load(request.get_json())
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
    #Logic to start the actually trigger a test will be implemented here on the next deliverable
    return jsonify(newTask), 201
