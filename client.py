import os.path as op
import sys
from urllib.parse import urlencode
import uuid

import requests


def get_machine_id():
    """Get the machine ID for the client. If it doesn't exist, create one."""
    if not op.exists(".machine_id"):
        machine_id = str(uuid.uuid4())
        with open(".machine_id", "w") as f:
            f.write(machine_id)
    with open(".machine_id", "r") as f:
        machine_id = f.read()
    return machine_id


def run(url):
    """Entry point for the client.

    Reads the username and password from STDIN, and sends a GET request to the server.
    """
    data = sys.stdin.read()
    try:
        username, password = data.splitlines()
    except ValueError:
        raise ValueError(
            (
                "Invalid input: This client expects exactly two lines from STDIN.",
                "Ensure that username and password are present in two lines,",
                "in the following format:\n '{username}\\n{password}'",
            )
        )
    machine_id = get_machine_id()
    auth_header = urlencode(
        {"username": username, "password": password, "machine_id": machine_id}
    )
    response = requests.get(url, headers={"SEEK-CUSTOM-AUTH": auth_header})
    print(response.content)  # NOQA: T201


if __name__ == "__main__":
    run(sys.argv[1])
