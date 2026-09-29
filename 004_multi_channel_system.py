tasks = []


def add_task(title, channel):
    title = title.strip()
    if not title:
        return "Task title cannot be empty."

    tasks.append(title)
    return f"Added '{title}' through {channel}."


def website_submit(form_title):
    return add_task(form_title, "website")


def mobile_submit(app_title):
    return add_task(app_title, "mobile app")


def chatbot_message(message):
    if not message.startswith("add "):
        return "Try: add followed by a task title"

    return add_task(message[4:], "chatbot")


print(website_submit("Write README"))
print(mobile_submit("Test the app"))
print(chatbot_message("add Publish to GitHub"))
print(tasks)