import os
import subprocess
import yaml
import sys
from deployer import login_to_dockerhub, build_push_docker_image

REPOSITORY = "sebasvucr/sebas"
TAGS = ["production-server-administrator-latest", "production-users-latest", "production-orchestrator-latest"]
DIRECTORY = ["serverAdministrator", "users", "orchestrator"]

def get_persistent_counter(name = "counter.txt"):
    """
    Escribe un texto junto a un contador persistente en un archivo de texto.
    El contador va de 0 a 2 y luego se reinicia a 0.
    Si el archivo no existe, lo crea.
    """
    try:
        with open(name, 'r') as f:
            counter_str = f.read().strip()
            # Intentar convertir a entero, si falla, asumir 0
            try:
                counter = int(counter_str)
            except ValueError:
                counter = 0 # Si el archivo está vacío o tiene algo no numérico
    except FileNotFoundError:
        counter = 0 
    # Actualizar el contador (0, 1, 2, 0, 1, 2...)
    new_counter = (counter + 1) % 3
    # Escribir el nuevo valor del contador en el archivo
    with open(name, 'w') as f:
        f.write(str(new_counter))  
    return counter

def main():
    docker_username = os.getenv('DOCKER_USERNAME')
    docker_password = os.getenv('DOCKER_PASSWORD')

    login_to_dockerhub(docker_username, docker_password)

    if not docker_username or not docker_password:
        print("Please set DOCKER_USERNAME and DOCKER_PASSWORD environment variables.")
        sys.exit(1)
    version = "Version2"
    counter = get_persistent_counter()
    base_path = os.path.join(version, "testOrchestrator", "services")

    complete_path = os.path.join(base_path, DIRECTORY[counter])
    build_push_docker_image(TAGS[counter], complete_path)


    print("\nDeployment script finished successfully!")

if __name__ == "__main__":
    main()

#cmd
#set DOCKER_USERNAME=sebasvucr
#set DOCKER_PASSWORD=****

#powershell
#$env:DOCKER_USERNAME = "sebasvucr"
#$env:DOCKER_PASSWORD = "***"

#docker tag production-orchestrator:latest sebasvucr/sebas:production-orchestrator-latest
#docker push sebasvucr/sebas:production-orchestrator-latest

#docker pull sebasvucr/sebas:production-orchestrator-latest