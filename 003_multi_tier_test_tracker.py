tasks = ["Write README", "Test the app"]

PERMISSIONS = {
    "member": {"view", "add", "complete"},
    "admin": {"view", "add", "complete", "delete"},
}


def can(user, action):
    return action in PERMISSIONS.get(user["role"], set())


def delete_task(user, title):
    if not can(user, "delete"):
        print(f"{user['name']} cannot delete tasks.")
        return

    if title in tasks:
        tasks.remove(title)
        print(f"{user['name']} deleted: {title}")
    else:
        print("Task not found.")


alex = {"name": "Alex", "role": "member"}
sam = {"name": "Sam", "role": "admin"}

delete_task(alex, "Write README")  # Permission denied
delete_task(sam, "Write README")   # Task deleted
print(tasks)                       # ['Test the app']
