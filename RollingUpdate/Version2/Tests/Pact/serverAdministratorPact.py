import pytest
import requests
from pact import Consumer, Provider

PACT_MOCK_HOST = 'localhost'
PACT_MOCK_PORT = 6000
PACT_URL = f'http://{PACT_MOCK_HOST}:{PACT_MOCK_PORT}'


@pytest.fixture(scope='module')
def pact():
    pact = Consumer('TaskConsumer').has_pact_with(
        Provider('TaskProvider'),
        host_name=PACT_MOCK_HOST,
        port=PACT_MOCK_PORT,
        log_dir='./logs',
        pact_dir='./pacts'
    )
    pact.start_service()
    yield pact
    pact.stop_service()


def test_get_all_servers_contract(pact):
    '''GET Test'''
    # Define the expected response body for the GET request
    expected_get_response = [
        {
            "id": 1,
            "info": [
                "Linux"
            ],
            "ip": "192.000.000",
            "name": "Server1"
        },
        {
            "id": 2,
            "info": [
                "8 cores"
            ],
            "ip": "192.000.001",
            "name": "Server2"
        },
        {
            "id": 3,
            "info": [
                "Desktop",
                "Windows"
            ],
            "ip": "192.000.002",
            "name": "Server3"
        }
    ]

    # Define the expected behavior of the mock for the GET request
    # You might want a different 'given' state if fetching all servers depends on existing data
    (pact
     .upon_receiving("Obtiene todos los servidores")
     .with_request("GET", "/servers/") # No body for a GET request
     .will_respond_with(200, body=expected_get_response))

    # Execute the code that makes the actual GET request
    with pact:
        response = requests.get(f"{PACT_URL}/servers/")
        assert response.status_code == 200
        assert response.json() == expected_get_response

def test_add_server_contract(pact):
    '''POST Test'''
    testBody = {
        "info": ["Linux"],
        "ip": "192.000.000",
        "name": "Servidor nuevo"
    }

    expected = {
        "id": 4,
        "name": "Servidor nuevo",
        "ip": "192.000.000",
        "info": ["Linux"],
    }

    # Definimos el comportamiento esperado del MOCK
    (pact
     .upon_receiving("Agregar servidor")
     .with_request("POST", "/servers/servers", body=testBody, headers={"Content-Type": "application/json"})
     .will_respond_with(201, body=expected))

    # Aquí se ejecuta el código que hace la solicitud a la API
    # y genera el PACT en JSON que luego se puede verificar
    with pact:
        response = requests.post(
            f"{PACT_URL}/servers/servers", json=testBody)
        assert response.status_code == 201
        assert response.json() == expected

def test_change_server_info_contract(pact):
    '''PUT Test'''
    testBody = {
        "info": ["New info"],
        "name": "Nuevo servidor"
    }

    expected = {
        "id": 1,
        "info": [
            "New info"
        ],
        "ip": "192.000.000",
        "name": "Nuevo servidor"
    }

    # Definimos el comportamiento esperado del MOCK
    (pact
     .upon_receiving("Cambiar info")
     .with_request("PUT", "/servers/servers/changeip/1", body=testBody, headers={"Content-Type": "application/json"})
     .will_respond_with(200, body=expected))

    # Aquí se ejecuta el código que hace la solicitud a la API
    # y genera el PACT en JSON que luego se puede verificar
    with pact:
        response = requests.put(
            f"{PACT_URL}/servers/servers/changeip/1", json=testBody)
        assert response.status_code == 200
        assert response.json() == expected

def test_change_info_server_not_found_contract(pact):
    '''PUT Test'''
    testBody = {
        "info": ["New info 99"],
        "name": "Nuevo servidor 99"
    }

    expected = {"error": "Server not found"}

    # Definimos el comportamiento esperado del MOCK
    (pact
     .upon_receiving("Cambiar info no encontrado")
     .with_request("PUT", "/servers/servers/changeip/99", body=testBody, headers={"Content-Type": "application/json"})
     .will_respond_with(404, body=expected))

    # Aquí se ejecuta el código que hace la solicitud a la API
    # y genera el PACT en JSON que luego se puede verificar
    with pact:
        response = requests.put(
            f"{PACT_URL}/servers/servers/changeip/99", json=testBody)
        assert response.status_code == 404
        assert response.json() == expected

def test_delete_server_contract(pact):
    '''DELETE Test'''
    # Definimos el comportamiento esperado del MOCK
    (pact
     .upon_receiving("Borrar servidor")
     .with_request("DELETE", "/servers/servers/1")
     .will_respond_with(204))

    # Aquí se ejecuta el código que hace la solicitud a la API
    # y genera el PACT en JSON que luego se puede verificar
    with pact:
        response = requests.delete(f"{PACT_URL}/servers/servers/1")
        assert response.status_code == 204
        assert not response.content

def test_delete_server_not_found_contract(pact):
    '''DELETE not found Test'''
    # Definimos el comportamiento esperado del MOCK
    (pact
     .upon_receiving("Borrar servidor no encontrado")
     .with_request("DELETE", "/servers/servers/99")
     .will_respond_with(404))

    # Aquí se ejecuta el código que hace la solicitud a la API
    # y genera el PACT en JSON que luego se puede verificar
    with pact:
        response = requests.delete(f"{PACT_URL}/servers/servers/99")
        assert response.status_code == 404
        assert not response.content
