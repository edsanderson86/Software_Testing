# Store the task titles in a shared list.
tasks = ["Write README", "Test the app"]

# Define which actions each role may perform.
# Members can view, add, and complete tasks; admins can also delete them.
PERMISSIONS = {
    "member": {"view", "add", "complete"},
    "admin": {"view", "add", "complete", "delete"},
}


def can(user, action):
    # Check whether the user's role allows the requested action.
    # Unrecognised roles receive no permissions.
    return action in PERMISSIONS.get(user["role"], set())


def delete_task(user, title):
    # Check permission before looking up or changing a task.
    if not can(user, "delete"):
        print(f"{user['name']} cannot delete tasks.")
        return

    # Remove the matching task if it exists.
    if title in tasks:
        tasks.remove(title)
        print(f"{user['name']} deleted: {title}")
    else:
        # Explain why an authorised deletion could not be completed.
        print("Task not found.")


# Create two example users with different access levels.
alex = {"name": "Alex", "role": "member"}
sam = {"name": "Sam", "role": "admin"}

# Alex's role does not allow deletion, so the task remains in the list.
delete_task(alex, "Write README")  # Alex cannot delete tasks.

# Sam's administrator role allows the task to be removed.
delete_task(sam, "Write README")   # Sam deleted: Write README

# Confirm that only the remaining task is listed.
print(tasks)                     # ['Test the app']