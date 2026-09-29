# test_scenario.py
# Scenario: A user adds a task, then marks it complete.

class TaskTracker:
    def __init__(self):
        self.tasks = []

    def add_task(self, title):
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be blank")

        self.tasks.append({"title": title, "completed": False})

    def complete_task(self, number):
        self.tasks[number - 1]["completed"] = True


def test_add_and_complete_task():
    tracker = TaskTracker()

    tracker.add_task("Write README")
    assert tracker.tasks == [
        {"title": "Write README", "completed": False}
    ]

    tracker.complete_task(1)
    assert tracker.tasks == [
        {"title": "Write README", "completed": True}
    ]


def test_blank_title_is_rejected():
    tracker = TaskTracker()

    try:
        tracker.add_task("   ")
    except ValueError:
        pass
    else:
        raise AssertionError("A blank title should be rejected")

    assert tracker.tasks == []


test_add_and_complete_task()
test_blank_title_is_rejected()
print("Both test scenarios passed")