# SQLite stores tasks in a local database file.
import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

# Create the Flask application.
app = Flask(__name__)

# Store the database beside this Python file so its location stays
# consistent regardless of where the application is launched.
DB_PATH = Path(__file__).with_name("tasks.db")


def get_connection():
    # Open a connection to the database, creating the file if needed.
    return sqlite3.connect(DB_PATH)


def create_table():
    # Create the tasks table on startup if it does not already exist.
    # Each task receives a unique ID and must have a title.
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL
            )
            """
        )


@app.get("/")
def show_tasks():
    # Retrieve saved tasks, showing the most recently added first.
    with get_connection() as connection:
        tasks = connection.execute(
            "SELECT id, title FROM tasks ORDER BY id DESC"
        ).fetchall()

    # Pass the task rows to the HTML template for display.
    return render_template("index.html", tasks=tasks)


@app.post("/tasks")
def add_task():
    # Read the submitted title and remove surrounding whitespace.
    title = request.form.get("title", "").strip()

    # Ignore empty titles, including submissions containing only spaces.
    if title:
        with get_connection() as connection:
            # Pass the title as a SQL parameter to handle user input safely.
            connection.execute(
                "INSERT INTO tasks (title) VALUES (?)", (title,)
            )

    # Return to the list after submission. Redirecting also prevents
    # a normal page refresh from submitting the same form again.
    return redirect(url_for("show_tasks"))


# Prepare the database before the application handles requests.
create_table()

if __name__ == "__main__":
    # Enable debugging for local development.
    app.run(debug=True)