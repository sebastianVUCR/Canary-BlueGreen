from locust import HttpUser, task, between
import json

#locust -f locust.py -H http://localhost:5000

class ServersTest(HttpUser):
    wait_time = between(1, 3)

    @task
    def get_servers(self):

        response = self.client.get("/servers") #para rolling update
        #response = self.client.get("http://localhost:5000/servers/servers/") # para blue green
        if response.status_code == 200:
            libros = json.loads(response.text)
            print(f"Obtuvimos una lista con {len(libros)} libros.")
        else:
            print("Failed to fetch.")

