tasks = []


# Increment 1: Add tasks
def add_task(title):
    tasks.append({"title": title, "completed": False})


# Increment 2: List tasks
def list_tasks():
    for number, task in enumerate(tasks, start=1):
        status = "✓" if task["completed"] else " "
        print(f"{number}. [{status}] {task['title']}")


# Increment 3: Complete a task
def complete_task(number):
    tasks[number - 1]["completed"] = True


add_task("Write README")
add_task("Test the app")
list_tasks()

print("\nAfter completing the first task:")
complete_task(1)
list_tasks()