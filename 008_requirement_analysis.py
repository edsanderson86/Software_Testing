# Group task storage and task operations in one reusable class.
class TaskTracker:
    def __init__(self):
        # Give each tracker its own independent task list.
        self.tasks = []

    def add_task(self, title):
        # Remove surrounding whitespace before checking the title.
        title = title.strip()
        if not title:
            # Reject blank titles without changing the stored tasks.
            raise ValueError("Task title cannot be blank")

        # Save valid tasks with an initial status of incomplete.
        self.tasks.append({"title": title, "completed": False})

    def complete_task(self, number):
        # Convert the displayed task number to a zero-based list index.
        # This example assumes the number refers to an existing task.
        self.tasks[number - 1]["completed"] = True


# Acceptance checks verify the behaviour required of the tracker.
tracker = TaskTracker()

# R1: Adding a valid task stores its title correctly.
tracker.add_task("Write README")
assert tracker.tasks[0]["title"] == "Write README"

# R2: A blank title must raise a validation error.
try:
    tracker.add_task("   ")
except ValueError:
    pass
else:
    raise AssertionError("R2 failed: blank title was accepted")

# R2: Rejecting a blank title must leave the task count unchanged.
assert len(tracker.tasks) == 1

# R3: Completing a task must update its completion status.
tracker.complete_task(1)
assert tracker.tasks[0]["completed"] is True

# Confirm that all acceptance checks above passed.
print("All requirements met")