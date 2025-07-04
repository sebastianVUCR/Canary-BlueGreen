import os
import subprocess
import yaml
import sys
from deployer import run_command
from rolling_update_deployer import get_persistent_counter

SERVICES = ["serverAdministrator", "users", "orchestrator"]
OLD_CONTAINER_NAME = ["serverAdministrator_v1", "uers_v1", "orchestrator_v1"]

def main():

    version = "Version2"
    os.chdir(version)
    counter = get_persistent_counter("counter_container.txt")
    run_command(["docker", "compose", "build", SERVICES[counter]])
    run_command(["docker", "stop", OLD_CONTAINER_NAME[counter]])
    run_command(["docker-compose", "up", "-d",OLD_CONTAINER_NAME[counter]])

    
    base_path = os.path.join(version, "testOrchestrator", "services")

    complete_path = os.path.join(base_path, SERVICES[counter])


    print("\nDeployment script finished successfully!")

if __name__ == "__main__":
    main()
