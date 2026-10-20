# test_scenario_execution.py
# Run a user scenario with visible progress and checks at each step.

class TaskTracker:
    def __init__(self):
        # Give each tracker an independent task list.
        self.tasks = []

    def add_task(self, title):
        # Remove surrounding whitespace and reject blank titles.
        title = title.strip()
        if not title:
            raise ValueError("Task title cannot be blank")

        # New tasks start as incomplete.
        self.tasks.append({"title": title, "completed": False})

    def complete_task(self, number):
        # Convert the displayed task number to a zero-based list index.
        # This example assumes the number identifies an existing task.
        self.tasks[number - 1]["completed"] = True


def run_scenario():
    # Start with a fresh tracker for a repeatable scenario.
    tracker = TaskTracker()

    print("Step 1: Add a task")
    tracker.add_task("Write README")

    # Check that the task has the expected title and initial status.
    assert tracker.tasks == [
        {"title": "Write README", "completed": False}
    ]
    print("PASS: Task was added as incomplete")

    print("Step 2: Complete the task")
    tracker.complete_task(1)

    # Check that completion changes the status and preserves the title.
    assert tracker.tasks == [
        {"title": "Write README", "completed": True}
    ]
    print("PASS: Task is complete")

    # Report success only after both checks pass.
    print("Result: TEST SCENARIO PASSED")


if __name__ == "__main__":
    # Run the scenario when executed directly, but not when imported.
    run_scenario()