# Use SQLite to save tasks between application runs.
import sqlite3


class TaskStore:
    def __init__(self, database_path):
        # Keep the database location for subsequent read and write operations.
        self.database_path = database_path

        # Prepare the table without replacing any existing tasks.
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
            # Each task has a unique ID, a required title, and a completion
            #