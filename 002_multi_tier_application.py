task-tracker-web/
├── app.py
└── templates/
    └── index.html

import sqlite3
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("tasks.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_table():
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
    with get_connection() as connection:
        tasks = connection.execute(
            "SELECT id, title FROM tasks ORDER BY id DESC"
        ).fetchall()

    return render_template("index.html", tasks=tasks)


@app.post("/tasks")
def add_task():
    title = request.form.get("title", "").strip()

    if title:
        with get_connection() as connection:
            connection.execute(
                "INSERT INTO tasks (title) VALUES (?)", (title,)
            )

    return redirect(url_for("show_tasks"))


create_table()

if __name__ == "__main__":
    app.run(debug=True)
    
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Task Tracker</title>
</head>
<body>
    <h1>My tasks</h1>

    <form action="/tasks" method="post">
        <label for="title">New task</label>
        <input id="title" name="title" required>
        <button type="submit">Add task</button>
    </form>

    <ul>
        {% for task in tasks %}
            <li>{{ task[1] }}</li>
        {% else %}
            <li>No tasks yet.</li>
        {% endfor %}
    </ul>
</body>
</html>

  python -m pip install Flask
python app.py  