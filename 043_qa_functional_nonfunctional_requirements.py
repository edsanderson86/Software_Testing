# functional_nonfunctional_requirements.py
# Run with: python functional_nonfunctional_requirements.py
# Demonstrate checks linked to functional and non-functional requirements.
# Functional requirements describe capabilities; non-functional requirements
# describe quality attributes and constraints. Their classification can overlap.

import time


class TaskService:
    def __init__(self):
        # Keep task data and sign-in state separate for each service instance.
        self.tasks = []
        self.logged_in = False

    def sign_in(self, username, password):
        # Compare credentials with fixed demonstration values.
        # This models sign-in without a user database or session tokens.
        self.logged_in = (
            username == "tester"
            and password == "example-password"
        )
        return self.logged_in

    def add_task(self, title):
        # Require sign-in before accepting a task.
        if not self.logged_in:
            raise PermissionError("Sign in required")

        # Remove surrounding whitespace and reject blank titles.
        title = title.strip()
        if not title:
            raise ValueError("Task title required")

        self.tasks.append(title)
        return title

    def list_tasks(self):
        # Apply the same sign-in requirement when retrieving tasks.
        if not self.logged_in:
            raise PermissionError("Sign in required")

        # Return a copy so callers cannot directly modify the stored list.
        return list(self.tasks)


def check(requirement_id, description, test):
    # Run the supplied verification function and print its outcome.
    try:
        test()
    except Exception as error:
        # Continue to later checks after reporting a failure.
        # Printed failures do not set a nonzero process exit code.
        print(f"FAIL {requirement_id}: {description} — {error}")
    else:
        print(f"PASS {requirement_id}: {description}")


# Functional check: verify that the supplied valid credentials permit sign-in.
def fr_01_sign_in():
    app = TaskService()
    assert app.sign_in("tester", "example-password")


# Functional check: verify task creation and subsequent retrieval.
def fr_02_add_task():
    app = TaskService()
    app.sign_in("tester", "example-password")
    assert app.add_task("Write README") == "Write README"
    assert app.list_tasks() == ["Write README"]


# Functional check: verify that a whitespace-only title raises an error.
def fr_03_reject_blank_title():
    app = TaskService()
    app.sign_in("tester", "example-password")

    try:
        app.add_task("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("Blank title was accepted")


# Security-related check: verify that task retrieval requires sign-in.
# Anonymous task creation is also restricted, but is not checked here.
def nfr_01_access_control():
    app = TaskService()

    try:
        app.list_tasks()
    except PermissionError:
        pass
    else:
        raise AssertionError("Anonymous access was allowed")


# Performance-related check: time one local method call.
def nfr_02_response_time():
    app = TaskService()
    app.sign_in("tester", "example-password")

    # Use a monotonic performance timer around the operation being measured.
    started = time.perf_counter()
    app.add_task("Test speed")
    elapsed_ms = (time.perf_counter() - started) * 1000

    # Apply a demonstration threshold of one second.
    # One in-memory operation does not establish performance under load.
    assert elapsed_ms < 1000, f"Took {elapsed_ms:.2f} ms"


# Isolation check: confirm that separate instances have independent task lists.
# Both instances use the same credentials; this does not verify account-level
# authorization within a shared service.
def nfr_03_data_isolation():
    first_user = TaskService()
    second_user = TaskService()

    first_user.sign_in("tester", "example-password")
    second_user.sign_in("tester", "example-password")

    first_user.add_task("Private task")
    assert second_user.list_tasks() == []


# Associate each requirement identifier and description with its check.
# Store function references here and execute them in the loop below.
requirements = [
    ("FR-01", "A user can sign in", fr_01_sign_in),
    ("FR-02", "A user can add and view a task", fr_02_add_task),
    ("FR-03", "Blank task titles are rejected", fr_03_reject_blank_title),
    ("NFR-01", "Unauthenticated access is denied", nfr_01_access_control),
    (
        "NFR-02",
        "A local add request completes within 1 second",
        nfr_02_response_time,
    ),
    (
        "NFR-03",
        "Separate service instances do not share tasks",
        nfr_03_data_isolation,
    ),
]

# Execute each requirement check and display its individual result.
# Run Python normally because optimized mode disables assert statements.
for requirement_id, description, test in requirements:
    check(requirement_id, description, test)