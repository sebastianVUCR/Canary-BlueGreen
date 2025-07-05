import os
import subprocess
import yaml
import sys
from deployer import run_command
from rolling_update_deployer import get_persistent_counter

SERVICES = ["serveradministrator", "users", "orchestrator"]
OLD_CONTAINER_NAME = ["serverAdministrator_v1", "users_v1", "orchestrator_v1"]

def main():

    version = "Version2"
    os.chdir(version)
    counter = get_persistent_counter("counter_container.txt")
    run_command(["docker", "compose", "build", SERVICES[counter]])
    run_command(["docker", "stop", OLD_CONTAINER_NAME[counter]])
    run_command(["docker-compose", "up", "-d",  SERVICES[counter]])
    print("\nDeployment script finished successfully!")

if __name__ == "__main__":
    main()

#resultados 529 fallos 1000 usuarios de 1 a 3 segundos.

#resultados 385 fallos 500 usuarios de 1 a 3 segundos

#blue green 3 fallos 500 usuarios de 1 a 3 segundos.
