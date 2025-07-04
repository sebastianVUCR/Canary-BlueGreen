import os
import subprocess
import yaml
import sys

REPOSITORY = "sebasvucr/sebas"

def run_command(command, cwd=None, input_str=None, error_message="Command failed"):
    """
    Runs a shell command and prints its output.
    Handles stdin input if provided. Exits on failure.
    """
    print(f"--> {' '.join(command)}")
    try:
        result = subprocess.run(
            command,
            input=input_str,  # Pass input_str directly to subprocess.run
            check=True,       # Raises CalledProcessError on non-zero exit code
            capture_output=True,
            text=True,        # Decodes stdout/stderr as text
            cwd=cwd
        )

        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip(), file=sys.stderr)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}", file=sys.stderr)
        print(f"Command failed with exit code {e.returncode}: {' '.join(e.cmd)}", file=sys.stderr)
        if e.stderr:
            print(f"Stderr: {e.stderr.strip()}", file=sys.stderr)
        if e.stdout:
            print(f"Stdout: {e.stdout.strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Command '{command[0]}' not found. Is it installed and in your PATH?", file=sys.stderr)
        sys.exit(1)

def login_to_dockerhub(username, password):
    """Logs into Docker Hub."""
    print("Logging into Docker Hub...")
    run_command(
        ["docker", "login", "-u", username, "--password-stdin"],
        input_str=password + "\n", 
        error_message="Failed to log in to Docker Hub."
    )
    print("Docker Hub login successful.")

def build_push_docker_image(tag, build_context_path):
    """Pushes Docker images to Docker Hub."""
    run_command(["docker", "build", "-t", f"{REPOSITORY}:{tag}", build_context_path])
    print(f"Image {tag} built successfully.")
    run_command(["docker", "push", f"{REPOSITORY}:{tag}"])
    print(f"Image {tag} pushed successfully.")


def main():
    docker_username = os.getenv('DOCKER_USERNAME')
    docker_password = os.getenv('DOCKER_PASSWORD')

    if not docker_username or not docker_password:
        print("Please set DOCKER_USERNAME and DOCKER_PASSWORD environment variables.")
        sys.exit(1)
    version = "Version1"
    base_path = os.path.join(version, "testOrchestrator", "services")
    complete_path = os.path.join(base_path, "orchestrator")

    login_to_dockerhub(docker_username, docker_password)
    build_push_docker_image("production-orchestrator-latest", complete_path)

    # complete_path = os.path.join(base_path, "serverAdministrator")
    # build_push_docker_image("production-server-administrator-latest", complete_path)

    # complete_path = os.path.join(base_path, "users")
    # build_push_docker_image("production-users-latest", complete_path)

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