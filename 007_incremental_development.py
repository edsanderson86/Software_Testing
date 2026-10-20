# Store each task as a dictionary containing its title and completion status.
tasks = []


# Increment 1: Allow users to add tasks.
def add_task(title):
    # New tasks start as incomplete.
    tasks.append({"title": title, "completed": False})


# Increment 2: Display tasks with numbers and completion indicators.
def list_tasks():
    # Start numbering at 1 so users can identify tasks easily.
    for number, task in enumerate(tasks, start=1):
        # Show a tick for completed tasks and a space for unfinished tasks.
        status = "✓" if task["completed"] else " "
        print(f"{number}. [{status}] {task['title']}")


# Increment 3: Mark a task as completed while keeping it in the list.
def complete_task(number):
    # Convert the displayed task number to Python's zero-based list index.
    # This example assumes the supplied number refers to an existing task.
    tasks[number - 1]["completed"] = True


# Add two example tasks and display their initial status.
add_task("Write README")
add_task("Test the app")
list_tasks()
# 1. [ ] Write README
# 2. [ ] Test the app

# Complete the first task and display the updated list.
print("\nAfter completing the first task:")
complete_task(1)
list_tasks()
# 1. [✓] Write README
# 2. [ ] Test the app