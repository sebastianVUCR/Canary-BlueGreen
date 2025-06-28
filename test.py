import os
import subprocess
import sys
import argparse # Import argparse for better command-line argument parsing

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
    """Logs into Docker Hub by passing password via stdin."""
    print("Attempting to log in to Docker Hub...")
    try:
        # Use Popen to allow passing password via stdin
        process = subprocess.Popen(
            ["docker", "login", "-u", username, "--password-stdin"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True  # Use text mode for strings
        )
        # Communicate with the process, sending the password to stdin
        stdout, stderr = process.communicate(input=password + "\n") # Add newline for stdin

        print(stdout)
        if stderr:
            print(stderr)

        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args, stdout, stderr)

    except subprocess.CalledProcessError as e:
        print(f"Error logging into Docker Hub. Exit code: {e.returncode}")
        print(f"Stderr: {e.stderr}")
        print(f"Stdout: {e.stdout}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: 'docker' command not found. Is Docker installed and in your PATH?")
        sys.exit(1)

    print("Successfully logged into Docker Hub.")

def build_and_push_single_image(docker_username, image_repo_name, build_context_path, image_tag):
    """
    Builds a single Docker image from a Dockerfile and pushes it to Docker Hub.
    
    Args:
        docker_username (str): The Docker Hub username.
        image_repo_name (str): The desired repository name (e.g., "production/serveradministrator").
                               This will be prefixed with the docker_username.
        build_context_path (str): The path to the directory containing the Dockerfile
                                  and context files for the build.
        image_tag (str): The tag to apply to the image (e.g., "latest", "v1.0").
    """
    full_image_name = f"{docker_username}/{image_repo_name}:{image_tag}"
    
    print(f"\n--- Processing Image: {full_image_name} ---")

    # 1. Build the image
    print(f"Building Docker image: {full_image_name} from context: {build_context_path}...")
    # The build context '.' assumes the Dockerfile is directly in build_context_path
    run_command(["docker", "build", "-t", full_image_name, build_context_path])
    print(f"Image {full_image_name} built successfully.")

    # 2. Push the image
    print(f"Pushing image: {full_image_name} to Docker Hub...")
    run_command(["docker", "push", full_image_name])
    print(f"Image {full_image_name} pushed successfully.")
    print(f"--- Finished Image: {full_image_name} ---\n")

def main():
    parser = argparse.ArgumentParser(description="Docker image deployment script.")
    parser.add_argument("tag", help="The tag to apply to the Docker images (e.g., 'latest', 'v1.0').")
    args = parser.parse_args()

    docker_username = os.getenv('DOCKER_USERNAME')
    docker_password = os.getenv('DOCKER_PASSWORD')

    if not docker_username or not docker_password:
        print("Error: Please set DOCKER_USERNAME and DOCKER_PASSWORD environment variables.")
        print("Example (Linux/macOS):")
        print("  export DOCKER_USERNAME=\"your_username\"")
        print("  export DOCKER_PASSWORD=\"your_password\"")
        print("Example (Windows CMD):")
        print("  set DOCKER_USERNAME=\"your_username\"")
        print("  set DOCKER_PASSWORD=\"your_password\"")
        print("Example (Windows PowerShell):")
        print("  $env:DOCKER_USERNAME=\"your_username\"")
        print("  $env:DOCKER_PASSWORD=\"your_password\"")
        sys.exit(1)

    # List of images to build and push.
    images_to_deploy = [
        {"image_repo_name": "production/serveradministrator", "build_context": "./testOrchestrator/services/serverAdministrator"},
        {"image_repo_name": "production/users", "build_context": "./testOrchestrator/services/users"},
        {"image_repo_name": "production/orchestrator", "build_context": "./testOrchestrator/services/orchestrator"},
    ]

    # Login to Docker Hub once
    login_to_dockerhub(docker_username, docker_password)

    # Iterate and build/push each image
    for img_info in images_to_deploy:
        # Ensure build context path exists
        full_build_context_path = os.path.join(os.path.dirname(__file__), img_info["build_context"])
        if not os.path.isdir(full_build_context_path):
            print(f"Error: Build context directory not found: {full_build_context_path}")
            print("Please ensure your project structure matches the paths defined in 'images_to_deploy'.")
            sys.exit(1)

        build_and_push_single_image(
            docker_username=docker_username,
            image_repo_name=img_info["image_repo_name"],
            build_context_path=img_info["build_context"], # Pass relative path for command context
            image_tag=args.tag # Use the tag from command-line argument
        )

    print("\n--- All specified Docker images built and pushed successfully! ---")

if __name__ == "__main__":
    main()