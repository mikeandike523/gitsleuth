from typing import List
import time
import subprocess
import sys

from termcolor import colored

SUBPROCESS_OUTPUT_MONITORING_INTERVAL = 0.1

def run_command_with_monitoring(command: List[str], **Popen_kwargs):
    try:
        # Run the command using subprocess.Popen with stdout and stderr pipes
        process = subprocess.Popen(command, **Popen_kwargs)

        while True:
            # Read a chunk of stdout
            stdout_chunk = process.stdout.read(1)
            if stdout_chunk:
                print(f"{stdout_chunk.decode()}",end="")

            # Read a chunk of stderr
            stderr_chunk = process.stderr.read(1)
            if stderr_chunk:
                sys.stderr.write(colored(f"{stderr_chunk.decode()}","red"))

            # Sleep for a short interval (adjust as needed)
            time.sleep(SUBPROCESS_OUTPUT_MONITORING_INTERVAL)

            # Check if the process has finished
            if process.poll() is not None:
                break

        # Get the return code of the process
        return_code = process.returncode

        if return_code == 0:
            print(f"\nCommand '{' '.join(command)}' executed successfully.")
        else:
            sys.stderr.write(colored(f"\nCommand '{' '.join(command)}' failed with return code {return_code}","red"))
            sys.stderr.write("\n")

    except Exception as e:
        sys.stderr.write(colored(f"\nError running command '{' '.join(command)}': {str(e)}"))
        sys.stderr.write("\n")
