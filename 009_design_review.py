import sqlite3


class TaskStore:
    def __init__(self, database_path):
        self.database_path = database_path

        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    completed INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def add(self, title):
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be blank")

        with sqlite3.connect(self.database_path) as connection:
            connection.execute(
                "INSERT INTO tasks (title) VALUES (?)",
                (title,),
            )

    def list_tasks(self):
        with sqlite3.connect(self.database_path) as connection:
            return connection.execute(
                "SELECT id, title, completed FROM tasks ORDER BY id"
            ).fetchall()


store = TaskStore("review_tasks.db")
store.add("Write README")
print(store.list_tasks())

# Open the database again to demonstrate that the task was saved.
reopened_store = TaskStore("review_tasks.db")
print("After reopening:", reopened_store.list_tasks())