import argparse
import os
import sqlite3
from urllib.parse import parse_qs

from bcrypt import hashpw
from flask import Flask, request, current_app


def init_db():
    db_path = current_app.config["DB_PATH"]
    if not os.path.exists(db_path):
        with sqlite3.connect(db_path) as conn:
            conn.execute(
                """
                CREATE TABLE users (
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    machine_id TEXT NULLABLE
                );
            """
            )


def login(auth):
    db_path = current_app.config["DB_PATH"]
    username, password, machine_id = (
        auth["username"],
        auth["password"],
        auth["machine_id"],
    )
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT machine_id FROM users WHERE username = ? AND password = ?",
            (username, password),
        )
        result = cursor.fetchone()
        if result:
            if result[0] is None:  # Machine ID not present
                # Check if the submitted machine ID exists for a different user
                cursor.execute(
                    "SELECT username FROM users WHERE machine_id = ?",
                    (machine_id,),
                )
                result = cursor.fetchone()
                if result:
                    return False
                cursor.execute(
                    "UPDATE users SET machine_id = ? WHERE username = ? AND password = ?",
                    (machine_id, username, password),
                )
                conn.commit()
                return True
            # Otherwhise check if it's the correct machine_id
            return result[0] == machine_id
        return False


def index():
    auth = request.headers.get("Seek-Custom-Auth")
    if not auth:
        return "Bad Request: Authentication header 'Seek-Custom-Auth' not found.", 400
    auth = {k: v[0] for k, v in parse_qs(auth).items()}
    for key in ["username", "password", "machine_id"]:
        if key not in auth:
            return f"Bad Request: Missing key '{key}' in authentication header.", 400
    auth["password"] = hashpw(auth["password"].encode(), current_app.config["SALT"])
    if login(auth):
        return "OK"
    return "Unauthorized", 401


def add_user(username, password):
    db_path = current_app.config["DB_PATH"]
    password = hashpw(password.encode(), current_app.config["SALT"])
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )
        conn.commit()


def update_password(username, new_password):
    db_path = current_app.config["DB_PATH"]
    new_password = hashpw(new_password.encode(), current_app.config["SALT"])
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password = ? WHERE username = ?", (new_password, username)
        )
        conn.commit()


def delete_user(username):
    db_path = current_app.config["DB_PATH"]
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()


def make_cli():
    """Make an argparse object for the CLI.

    1. Run the flask server (default)
    2. Add a username and password
    3. Update the password for a user
    4. Delete a user
    """
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("run_server", help="Run the Flask server (default operation)")

    add_parser = subparsers.add_parser("add_user", help="Add a username and password")
    add_parser.add_argument("username", help="Username to add")
    add_parser.add_argument("password", help="Password for the username")

    update_parser = subparsers.add_parser(
        "update_pw", help="Update the password for an existing user"
    )
    update_parser.add_argument("username", help="Username to update")
    update_parser.add_argument("new_password", help="New password for the username")

    delete_parser = subparsers.add_parser("delete_user", help="Delete a user")
    delete_parser.add_argument("username", help="Username to delete")
    return parser


def make_app(db_path="auth.db", salt=b"$2b$12$emU0Je9vTNLx9RzvGe/go.", **kwargs):
    app = Flask(__name__)
    app.config.update({"SALT": salt, "DB_PATH": db_path, **kwargs})
    app.add_url_rule("/check", view_func=index, methods=["GET"])
    with app.app_context():
        init_db()
    return app


def main():
    app = make_app()
    cli = make_cli()
    args = cli.parse_args()
    if args.command is None or args.command == "run_server":
        app.run(debug=True)
    elif args.command == "add_user":
        with app.app_context():
            add_user(args.username, args.password)
    elif args.command == "update_pw":
        with app.app_context():
            update_password(args.username, args.new_password)
    elif args.command == "delete_user":
        with app.app_context():
            delete_user(args.username)
    else:
        raise ValueError(f"Invalid command: {args.command}")


if __name__ == "__main__":
    main()
