# test_scenario.py
# Verify that users can add and complete a task,
# and that blank titles are rejected.

class TaskTracker:
    def __init__(self):
        # Keep each tracker's tasks separate.
        self.tasks = []

    def add_task(self, title):
        # Remove surrounding spaces and reject empty titles.
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be blank")

        # Store the task as incomplete until it is marked complete.
        self.tasks.append({"title": title, "completed": False})

    def complete_task(self, number):
        # Convert the task number to Python's zero-based list index.
        # This example assumes the number identifies an existing task.
        self.tasks[number - 1]["completed"] = True


def test_add_and_complete_task():
    # Start with a fresh tracker for this scenario.
    tracker = TaskTracker()

    # Verify that adding a task saves its title and initial status.
    tracker.add_task("Write README")
    assert tracker.tasks == [
        {"title": "Write README", "completed": False}
    ]

    # Verify that completing the task updates its status
    # while preserving its title and position in the list.
    tracker.complete_task(1)
    assert tracker.tasks == [
        {"title": "Write README", "completed": True}
    ]


def test_blank_title_is_rejected():
    # Use a separate tracker so this test has no shared state.
    tracker = TaskTracker()

    # A whitespace-only title must raise a validation error.
    try:
        tracker.add_task("   ")
    except ValueError:
        pass
    else:
        # Fail the test if no validation error was raised.
        raise AssertionError("A blank title should be rejected")

    # Confirm that the rejected submission added no task.
    assert tracker.tasks == []


# Run both scenarios; an uncaught error stops execution.
test_add_and_complete_task()
test_blank_title_is_rejected()

# Display confirmation only after both scenarios pass.
print("Both test scenarios passed")