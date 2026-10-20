# todo_test_scenarios.py
# Run with: python todo_test_scenarios.py
# Describe and execute five scenarios against an in-memory to-do list.
# Scenario steps describe user actions; checks call Python methods directly.

from dataclasses import dataclass


class TodoList:
    def __init__(self):
        # Give each instance its own task list.
        self.tasks = []

    def add(self, title):
        # Remove surrounding whitespace and reject blank titles.
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be blank")

        # Create an incomplete task and return the stored dictionary.
        # Using list length for IDs can produce duplicate IDs after deletions;
        # the scenarios below do not cover that sequence.
        task = {"id": len(self.tasks) + 1, "title": title, "done": False}
        self.tasks.append(task)
        return task

    def complete(self, task_id):
        # Mark the first task with the requested ID as complete.
        for task in self.tasks:
            if task["id"] == task_id:
                task["done"] = True
                return

        # Report an unknown ID without modifying any tasks.
        raise ValueError("Task not found")

    def delete(self, task_id):
        # Remove the first matching task and stop searching immediately.
        for task in self.tasks:
            if task["id"] == task_id:
                self.tasks.remove(task)
                return

        raise ValueError("Task not found")


# Pair readable scenario details with the function that verifies the outcome.
@dataclass
class Scenario:
    id: str
    title: str
    steps: str
    expected: str
    check: callable


def add_valid_task():
    # Start with a fresh list and verify the returned task's initial values.
    app = TodoList()
    task = app.add("Buy groceries")
    assert task["title"] == "Buy groceries"
    assert task["done"] is False


def reject_blank_title():
    # Verify that whitespace-only input raises an error.
    app = TodoList()
    try:
        app.add("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("Blank title was accepted")

    # Confirm that validation prevented the task from being stored.
    assert app.tasks == []


def complete_existing_task():
    # Create a task, complete it by ID, and inspect its updated state.
    # The returned dictionary references the same object stored in the list.
    app = TodoList()
    task = app.add("Write README")
    app.complete(task["id"])
    assert task["done"] is True


def delete_existing_task():
    # Delete the only task and verify that the list becomes empty.
    app = TodoList()
    task = app.add("Test the app")
    app.delete(task["id"])
    assert app.tasks == []


def reject_unknown_task():
    # Verify that completing an ID in an empty list raises an error.
    # This does not test preservation of existing tasks.
    app = TodoList()
    try:
        app.complete(999)
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown task was completed")


# Store function references without calling them during scenario definition.
scenarios = [
    Scenario(
        "TC-01",
        "Add a valid task",
        "Enter 'Buy groceries' and select Add",
        "The task appears as incomplete",
        add_valid_task,
    ),
    Scenario(
        "TC-02",
        "Reject a blank title",
        "Enter spaces and select Add",
        "An error appears and no task is added",
        reject_blank_title,
    ),
    Scenario(
        "TC-03",
        "Complete a task",
        "Add a task and select Complete",
        "The task is marked complete",
        complete_existing_task,
    ),
    Scenario(
        "TC-04",
        "Delete a task",
        "Add a task and select Delete",
        "The task disappears",
        delete_existing_task,
    ),
    Scenario(
        "TC-05",
        "Handle an unknown task ID",
        "Try to complete task 999",
        "An error appears and no task changes",
        reject_unknown_task,
    ),
]

# Display each scenario's intent before executing its check.
for scenario in scenarios:
    print(f"\n{scenario.id}: {scenario.title}")
    print("Steps:", scenario.steps)
    print("Expected:", scenario.expected)

    try:
        scenario.check()
    except Exception as error:
        # Report the failure and continue so later scenarios still run.
        # Failures are printed; they do not set a nonzero process exit code.
        print("Result: FAIL —", error)
    else:
        # Reaching this branch means the check raised no exception.
        print("Result: PASS")