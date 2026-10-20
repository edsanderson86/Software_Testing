# Iteration 1: Introduce basic task storage.
def add_task_v1(tasks, title):
    # Save the title exactly as supplied.
    tasks.append(title)


# Create a shared task list and demonstrate the first version.
tasks = []
add_task_v1(tasks, "Write README")
print("Version 1:", tasks)
# Version 1: ['Write README']


# Iteration 2: Improve task entry following feedback.
def add_task_v2(tasks, title):
    # Remove surrounding spaces to keep task titles consistent.
    title = title.strip()

    # Give useful feedback without saving an empty title.
    if not title:
        return "Please enter a task title."

    # Save the cleaned title and confirm success.
    tasks.append(title)
    return "Task added."


# Demonstrate both a valid submission and a rejected blank title.
print(add_task_v2(tasks, "  Test the app  "))
# Task added.

print(add_task_v2(tasks, "   "))
# Please enter a task title.

print("Version 2:", tasks)
# Version 2: ['Write README', 'Test the app']


# Iteration 3: Let users complete tasks.
def complete_task(tasks, title):
    # Check that the requested task exists before removing it.
    if title not in tasks:
        return "Task not found."

    # Completing a task removes it from the active list.
    # This version does not keep a history of completed tasks.
    tasks.remove(title)
    return f"Completed: {title}"


# Complete an existing task and display the remaining active tasks.
print(complete_task(tasks, "Write README"))
# Completed: Write README

print("Version 3:", tasks)
# Version 3: ['Test the app']