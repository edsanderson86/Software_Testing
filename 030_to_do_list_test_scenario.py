# todo_test_scenarios.py
# Run with: python todo_test_scenarios.py

from dataclasses import dataclass


class TodoList:
    def __init__(self):
        self.tasks = []

    def add(self, title):
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be blank")

        task = {"id": len(self.tasks) + 1, "title": title, "done": False}
        self.tasks.append(task)
        return task

    def complete(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                task["done"] = True
                return
        raise ValueError("Task not found")

    def delete(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                self.tasks.remove(task)
                return
        raise ValueError("Task not found")


@dataclass
class Scenario:
    id: str
    title: str
    steps: str
    expected: str
    check: callable


def add_valid_task():
    app = TodoList()
    task = app.add("Buy groceries")
    assert task["title"] == "Buy groceries"
    assert task["done"] is False


def reject_blank_title():
    app = TodoList()
    try:
        app.add("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("Blank title was accepted")
    assert app.tasks == []


def complete_existing_task():
    app = TodoList()
    task = app.add("Write README")
    app.complete(task["id"])
    assert task["done"] is True


def delete_existing_task():
    app = TodoList()
    task = app.add("Test the app")
    app.delete(task["id"])
    assert app.tasks == []


def reject_unknown_task():
    app = TodoList()
    try:
        app.complete(999)
    except ValueError:
        pass
    else:
        raise AssertionError("Unknown task was completed")


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

for scenario in scenarios:
    print(f"\n{scenario.id}: {scenario.title}")
    print("Steps:", scenario.steps)
    print("Expected:", scenario.expected)

    try:
        scenario.check()
    except Exception as error:
        print("Result: FAIL —", error)
    else:
        print("Result: PASS")