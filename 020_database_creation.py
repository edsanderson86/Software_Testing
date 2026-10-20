# database_example.py
# Run with: python database_example.py
# Demonstrate related tables, data insertion, filtering, joins, and updates.
# Each run drops and recreates the users, projects, and tasks tables,
# deleting any existing data in those tables in task_tracker.db.

import sqlite3

# Open the database, creating the file if it does not already exist.
connection = sqlite3.connect("task_tracker.db")

# Enforce foreign-key relationships for this connection.
connection.execute("PRAGMA foreign_keys = ON")

# Allow result columns to be accessed by name and converted to dictionaries.
connection.row_factory = sqlite3.Row

# Model users, projects, and tasks as separate entities.
# Columns hold attributes; primary keys uniquely identify records.
# Foreign keys connect each project to an owner and each task to a project.
#
# One user can own many projects; each project has one owner.
# One project can contain many tasks; each task belongs to one project.
#
# Drop child tables before parent tables to respect their dependencies.
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

# Insert parent records before records that reference them.
# The transaction commits on success and rolls back if an error occurs.
with connection:
    # Parameter placeholders keep supplied values separate from SQL syntax.
    connection.executemany(
        "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
        [
            (1, "Alex", "alex@example.test"),
            (2, "Sam", "sam@example.test"),
            # Leave Jo without a project to demonstrate a LEFT JOIN.
            (3, "Jo", "jo@example.test"),
        ],
    )

    # Connect each project to an existing user through owner_id.
    connection.executemany(
        "INSERT INTO projects (id, owner_id, name) VALUES (?, ?, ?)",
        [
            (10, 1, "Website"),
            (20, 2, "Mobile App"),
        ],
    )

    # Add tasks with varied priorities and statuses for the query examples.
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
    # Print a heading and display each result as column-value pairs.
    print(f"\n{label}")
    for row in connection.execute(sql, parameters):
        print(dict(row))


# Retrieve selected columns from every task.
# Without ORDER BY, the result order is not guaranteed.
show("SELECT all tasks", """
    SELECT id, title, priority, status
    FROM tasks
""")

# Filter records using a status supplied as a query parameter.
show("WHERE: one condition", """
    SELECT title, status
    FROM tasks
    WHERE status = ?
""", ("open",))

# Combine membership and numeric comparisons.
# BETWEEN includes both endpoints; these conditions select priorities 3 and 4.
# Some conditions overlap intentionally to demonstrate the different operators.
show("WHERE with IN, >, <, and BETWEEN", """
    SELECT title, priority
    FROM tasks
    WHERE status IN ('open', 'done')
      AND priority > 2
      AND priority < 5
      AND priority BETWEEN 3 AND 4
""")

# Use percent signs as wildcards to match text anywhere in the title.
show("LIKE: titles containing 'Test'", """
    SELECT title
    FROM tasks
    WHERE title LIKE ?
""", ("%Test%",))

# Select high-priority open tasks or the specifically named README task.
# Parentheses make the intended grouping explicit.
show("AND / OR: use parentheses to make precedence clear", """
    SELECT title, priority, status
    FROM tasks
    WHERE (status = 'open' AND priority >= 4)
       OR title = 'Write README'
""")

# Sort higher priorities first, then return at most two records.
show("LIMIT: retrieve at most two rows", """
    SELECT title, priority
    FROM tasks
    ORDER BY priority DESC
    LIMIT 2
""")

# Match tasks to their projects using the foreign-key relationship.
# Aliases provide readable column names in the displayed results.
show("INNER JOIN: tasks with their projects", """
    SELECT tasks.title AS task, projects.name AS project
    FROM tasks
    INNER JOIN projects ON tasks.project_id = projects.id
""")

# Follow both relationships to show each task, its project, and its owner.
show("Three-table INNER JOIN: tasks, projects, and owners", """
    SELECT tasks.title AS task,
           projects.name AS project,
           users.name AS owner
    FROM tasks
    INNER JOIN projects ON tasks.project_id = projects.id
    INNER JOIN users ON projects.owner_id = users.id
""")

# Keep every user, including those without a matching project.
# Jo's project value appears as None because SQL returns NULL.
show("LEFT JOIN: include users with no projects", """
    SELECT users.name AS user,
           projects.name AS project
    FROM users
    LEFT JOIN projects ON projects.owner_id = users.id
    ORDER BY users.id
""")

# Change only the task identified by the WHERE clause.
with connection:
    connection.execute(
        "UPDATE tasks SET status = ? WHERE id = ?",
        ("done", 101),
    )

# Retrieve the changed record to display its saved status.
show("After UPDATE", """
    SELECT id, title, status
    FROM tasks
    WHERE id = 101
""")

# Remove one task by its primary key, leaving other records unchanged.
with connection:
    connection.execute(
        "DELETE FROM tasks WHERE id = ?",
        (104,),
    )

# Display the remaining tasks in a defined order.
show("After DELETE", """
    SELECT id, title
    FROM tasks
    ORDER BY id
""")

# Release the database connection after all examples finish.
connection.close()