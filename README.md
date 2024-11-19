# flask-client-auth


Requirements
------------

* A client and a server script.
* Authentication through a header named `SEEK_CUSTOM_AUTH`, the header contains:
    - a username
    - a password
    - a unique machine ID which is not transferrable between computers
* The first time a client sends a request, the server associates the machine ID
  with the user. No other user should then be able to use this machine ID.
* Server has only a `/check` endpoint.
* Auth is successful only if:
    - The username and password are correct and a new machine ID is sent, or
    - an existing machine ID is sent with the correct username and password.
* The client accepts a username and password from STDIN, sends the request and
  prints the response.
* Backend should have a CLI to to add users and add or update passwords.
* Automated tests
