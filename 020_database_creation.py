# database_example.py
# Run with: python database_example.py

import sqlite3

# Creates a new database file if it does not already exist.
connection = sqlite3.connect("task_tracker.db")
connection.execute("PRAGMA foreign_keys = ON")
connection.row_factory = sqlite3.Row

# Each table is an entity.
# Each column is an attribute.
# id: primary key; owner_id/project_id: foreign keys.
# USERS 1-to-many PROJECTS; PROJECTS 1-to-many TASKS.
connection.executescript("""
DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id)
);
""")

# INSERT data.
with connection:
    connection.executemany(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        [
            (1, "Alex", "alex@example.test"),
            (2, "Sam", "sam@example.test"),
            (3, "Jo", "jo@example.test"),  # No project: useful for LEFT JOIN
        ],
    )
    connection.executemany(
        "INSERT INTO projects (id, owner_id, name) VALUES (?, ?, ?)",
        [
            (10, 1, "Website"),
            (20, 2, "Mobile App"),
        ],
    )
    connection.executemany(
        """
        INSERT INTO tasks (id, project_id, title, priority, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (101, 10, "Write README", 2, "open"),
            (102, 10, "Test login", 4, "open"),
            (103, 20, "Fix layout", 3, "done"),
            (104, 20, "Test offline mode", 5, "open"),
        ],
    )


def show(label, sql, parameters=()):
    print(f"\n{label}")
    for row in connection.execute(sql, parameters):
        print(dict(row))


show("SELECT all tasks", """
    SELECT id, title, priority, status
    FROM tasks
""")

show("WHERE: one condition", """
    SELECT title, status
    FROM tasks
    WHERE status = ?
""", ("open",))

show("WHERE with IN, >, <, and BETWEEN", """
    SELECT title, priority
    FROM tasks
    WHERE status IN ('open', 'done')
      AND priority > 2
      AND priority < 5
      AND priority BETWEEN 3 AND 4
""")

show("LIKE: titles containing 'Test'", """
    SELECT title
    FROM tasks
    WHERE title LIKE ?
""", ("%Test%",))

show("AND / OR: use parentheses to make precedence clear", """
    SELECT title, priority, status
    FROM tasks
    WHERE (status = 'open' AND priority >= 4)
       OR title = 'Write README'
""")

show("LIMIT: retrieve at most two rows", """
    SELECT title, priority
    FROM tasks
    ORDER BY priority DESC
    LIMIT 2
""")

show("INNER JOIN: tasks with their projects", """
    SELECT tasks.title AS task, projects.name AS project
    FROM tasks
    INNER JOIN projects ON tasks.project_id = projects.id
""")

show("Three-table INNER JOIN: tasks, projects, and owners", """
    SELECT tasks.title AS task,
           projects.name AS project,
           users.name AS owner
    FROM tasks
    INNER JOIN projects ON tasks.project_id = projects.id
    INNER JOIN users ON projects.owner_id = users.id
""")

show("LEFT JOIN: include users with no projects", """
    SELECT users.name AS user,
           projects.name AS project
    FROM users
    LEFT JOIN projects ON projects.owner_id = users.id
    ORDER BY users.id
""")

# UPDATE existing data.
with connection:
    connection.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        ("done", 101),
    )

show("After UPDATE", """
    SELECT id, title, status
    FROM tasks
    WHERE id = 101
""")

# DELETE selected data.
with connection:
    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (104,),
    )

show("After DELETE", """
    SELECT id, title
    FROM tasks
    ORDER BY id
""")

connection.close()