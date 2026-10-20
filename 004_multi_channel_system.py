# Store tasks submitted through any supported channel.
tasks = []


def add_task(title, channel):
    # Remove surrounding whitespace and reject empty titles.
    title = title.strip()
    if not title:
        return "Task title cannot be empty."

    # Save the task and confirm where it was submitted.
    tasks.append(title)
    return f"Added '{title}' through {channel}."


def website_submit(form_title):
    # Process website submissions using the shared validation rules.
    return add_task(form_title, "website")


def mobile_submit(app_title):
    # Process mobile submissions using the same task-creation logic.
    return add_task(app_title, "mobile app")


def command_submit(message):
    # Require the command prefix before accepting a task title.
    if not message.startswith("add "):
        return "Try: add followed by a task title"

    # Remove the prefix and pass the title to the shared function.
    return add_task(message[4:], "command interface")


# Demonstrate task creation through each supported channel.
print(website_submit("Write README"))
# Added 'Write README' through website.

print(mobile_submit("Test the app"))
# Added 'Test the app' through mobile app.

print(command_submit("add Publish to GitHub"))
# Added 'Publish to GitHub' through command interface.

# Display the combined list of tasks.
print(tasks)
# ['Write README', 'Test the app', 'Publish to GitHub']