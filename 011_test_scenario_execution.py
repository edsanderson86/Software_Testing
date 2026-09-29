# test_scenario_execution.py

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


def run_scenario():
    tracker = TaskTracker()

    print("Step 1: Add a task")
    tracker.add_task("Write README")
    assert tracker.tasks == [
        {"title": "Write README", "completed": False}
    ]
    print("PASS: Task was added as incomplete")

    print("Step 2: Complete the task")
    tracker.complete_task(1)
    assert tracker.tasks == [
        {"title": "Write README", "completed": True}
    ]
    print("PASS: Task is complete")

    print("Result: TEST SCENARIO PASSED")


if __name__ == "__main__":
    run_scenario()