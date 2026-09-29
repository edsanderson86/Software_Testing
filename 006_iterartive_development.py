# Iteration 1: Store and display tasks
def add_task_v1(tasks, title):
    tasks.append(title)


tasks = []
add_task_v1(tasks, "Write README")
print("Version 1:", tasks)


# Iteration 2: Improve the same feature after feedback:
# remove extra spaces and reject blank titles
def add_task_v2(tasks, title):
    title = title.strip()

    if not title:
        return "Please enter a task title."

    tasks.append(title)
    return "Task added."


print(add_task_v2(tasks, "  Test the app  "))
print(add_task_v2(tasks, "   "))
print("Version 2:", tasks)


# Iteration 3: Add another useful feature
def complete_task(tasks, title):
    if title not in tasks:
        return "Task not found."

    tasks.remove(title)
    return f"Completed: {title}"


print(complete_task(tasks, "Write README"))
print("Version 3:", tasks)