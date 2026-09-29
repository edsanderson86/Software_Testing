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


# Acceptance checks based on the requirements
tracker = TaskTracker()

tracker.add_task("Write README")
assert tracker.tasks[0]["title"] == "Write README"  # R1

try:
    tracker.add_task("   ")
except ValueError:
    pass
else:
    raise AssertionError("R2 failed: blank title was accepted")

assert len(tracker.tasks) == 1  # R2: nothing was added

tracker.complete_task(1)
assert tracker.tasks[0]["completed"] is True  # R3

print("All requirements met")