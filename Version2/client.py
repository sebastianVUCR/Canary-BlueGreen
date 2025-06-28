import pika
import requests
import time
import json
import http.client


# def callback(ch, method, properties, body):
#     print(f" [x] Received {body}")



def main():
    DEFAULT_SLEEP = 3
    taskRequestBody = {
    "retriggerCommand": "python --version",
    "serverID": "U8"
    }
    requestTaskExecution(taskRequestBody)
    time.sleep(DEFAULT_SLEEP)
    readMessages("tasksQueue")
    time.sleep(DEFAULT_SLEEP)

def readMessages(serviceQueue):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=serviceQueue)
    # channel.basic_consume(queue=serviceQueue, on_message_callback=callback, auto_ack=True)
    method_frame, properties, body = channel.basic_get(queue=serviceQueue, auto_ack=True)
    if method_frame:
        print(f"Mensaje recibido: {body.decode()}")
    # print(' [*] Waiting for messages. To exit press CTRL+C')
    # channel.start_consuming()

def requestTaskExecution(requestBody):
    ''''Sends a request to the orchestrator server'''
    conn = http.client.HTTPConnection("localhost", 5002)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    json_data = json.dumps(requestBody)

    conn.request("POST", "/tasks/tasks", body=json_data, headers=headers)
    response = conn.getresponse()

    print(f"Status: {response.status}")
    print(f"Reason: {response.reason}")
    response_data = response.read().decode("utf-8")
    print(f"Response Data: {response_data}")

    conn.close()

if __name__ == '__main__':
    main()