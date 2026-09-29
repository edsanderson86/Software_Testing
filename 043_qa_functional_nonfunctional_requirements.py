# functional_nonfunctional_requirements.py
# Run with: python functional_nonfunctional_requirements.py

import time


class TaskService:
    def __init__(self):
        self.tasks = []
        self.logged_in = False

    def sign_in(self, username, password):
        self.logged_in = (
            username == "tester"
            and password == "example-password"
        )
        return self.logged_in

    def add_task(self, title):
        if not self.logged_in:
            raise PermissionError("Sign in required")

        title = title.strip()
        if not title:
            raise ValueError("Task title required")

        self.tasks.append(title)
        return title

    def list_tasks(self):
        if not self.logged_in:
            raise PermissionError("Sign in required")
        return list(self.tasks)


def check(requirement_id, description, test):
    try:
        test()
    except Exception as error:
        print(f"FAIL {requirement_id}: {description} — {error}")
    else:
        print(f"PASS {requirement_id}: {description}")


# Functional requirement: what the system must do.
def fr_01_sign_in():
    app = TaskService()
    assert app.sign_in("tester", "example-password")


def fr_02_add_task():
    app = TaskService()
    app.sign_in("tester", "example-password")
    assert app.add_task("Write README") == "Write README"
    assert app.list_tasks() == ["Write README"]


def fr_03_reject_blank_title():
    app = TaskService()
    app.sign_in("tester", "example-password")

    try:
        app.add_task("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("Blank title was accepted")


# Non-functional requirement: how well or under what constraints it works.
def nfr_01_access_control():
    app = TaskService()

    try:
        app.list_tasks()
    except PermissionError:
        pass
    else:
        raise AssertionError("Anonymous access was allowed")


def nfr_02_response_time():
    app = TaskService()
    app.sign_in("tester", "example-password")

    started = time.perf_counter()
    app.add_task("Test speed")
    elapsed_ms = (time.perf_counter() - started) * 1000

    # A local example threshold, not a production performance target.
    assert elapsed_ms < 1000, f"Took {elapsed_ms:.2f} ms"


def nfr_03_data_isolation():
    first_user = TaskService()
    second_user = TaskService()

    first_user.sign_in("tester", "example-password")
    second_user.sign_in("tester", "example-password")

    first_user.add_task("Private task")
    assert second_user.list_tasks() == []


requirements = [
    ("FR-01", "A user can sign in", fr_01_sign_in),
    ("FR-02", "A user can add and view a task", fr_02_add_task),
    ("FR-03", "Blank task titles are rejected", fr_03_reject_blank_title),
    ("NFR-01", "Unauthenticated access is denied", nfr_01_access_control),
    ("NFR-02", "A local add request completes within 1 second", nfr_02_response_time),
    ("NFR-03", "Separate service instances do not share tasks", nfr_03_data_isolation),
]

for requirement_id, description, test in requirements:
    check(requirement_id, description, test) 