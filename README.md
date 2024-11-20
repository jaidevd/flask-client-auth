# flask-client-auth


## Installation requirements

Please run the following command to install dependencies:

```bash
pip install flask requests bcrypt
```

## Usage

There are two parts of interest in this project, the server and the client,
both available as Python modules.

### Server
The server script is fundamentally a CLI, and can do one of the following at a
time:

* Run a flask server (default)
* Add a user
* Update a user's password
* Delete a user

Please run the following command for more details:

```bash
$ python server.py -h
```

E.g. to add users, run the following command:

```bash
$ python server.py add_user <username> <password>
```

and to run the server, run the following command:

```bash
$ python server.py
```

### Client

The client script reads the username and password from STDIN, sends a request to
a URL specified through a command line argument, and prints the response.

E.g. to send a request with a username `user` and password `pass` to a url
(which could be `http://localhost:5000/check` while developing this app),
run the following command:

```bash
echo "user\npass" | python client.py http://localhost:5000/check
```

This prints the response if the server is running at the specified URL.

**Note:** The username and password have to be read through STDIN, separated by a newline.

## Testing

Run tests for the backend with the following command:

```bash
$ python tests.py
```

---


#### Assignment Requirements (for my reference)

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
