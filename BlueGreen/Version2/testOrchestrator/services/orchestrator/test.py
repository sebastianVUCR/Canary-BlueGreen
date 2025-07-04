import sys
import subprocess

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
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error executing command: {command}", file=sys.stderr)
            print(result.stderr, file=sys.stderr)
            sys.exit(result.returncode)
        else:
            print(result.stdout)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

execute_command("cmd /c echo hola")