# user_interface_testing.py
# Install: python -m pip install selenium
# Run: python user_interface_testing.py
# Requires Chrome installed on your computer.
# Check page content, control states, input labeling, and task creation.
# Tasks exist only in the page and are lost when it is reloaded.

from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Define a self-contained page with a labeled input, validation feedback,
# and JavaScript that adds task titles to the displayed list.
html = """
<!doctype html>
<html>
<head>
    <title>To-Do List</title>
    <style>
        body { font-family: sans-serif; max-width: 500px; margin: 40px auto; }
        button { cursor: pointer; }
        .error { color: darkred; }
    </style>
</head>
<body>
    <h1>To-Do List</h1>

    <label for="task-title">Task title</label>
    <input id="task-title" type="text">
    <button id="add-task" type="button">Add task</button>

    <p id="error" class="error" role="alert"></p>
    <ul id="tasks"></ul>

    <script>
        document.getElementById("add-task").addEventListener("click", () => {
            const input = document.getElementById("task-title");
            const title = input.value.trim();
            const error = document.getElementById("error");

            if (!title) {
                error.textContent = "Enter a task title";
                return;
            }

            error.textContent = "";
            const item = document.createElement("li");
            item.textContent = title;
            document.getElementById("tasks").appendChild(item);
            input.value = "";
        });
    </script>
</body>
</html>
"""

# Launch Chrome and allow up to five seconds for explicit wait conditions.
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

try:
    # Load the encoded page directly without starting a web server.
    driver.get("data:text/html;charset=utf-8," + quote(html))

    # Verify the page identity, input visibility, and button's enabled state.
    # These checks do not assess the page's overall visual layout.
    assert driver.title == "To-Do List"
    assert driver.find_element(By.TAG_NAME, "h1").text == "To-Do List"
    assert driver.find_element(By.ID, "task-title").is_displayed()
    assert driver.find_element(By.ID, "add-task").is_enabled()
    print("Page content and controls: PASS")

    # Check that a label references the input's ID and has the expected text.
    # This is one accessibility check, not a complete accessibility assessment.
    label = driver.find_element(By.CSS_SELECTOR, "label[for='task-title']")
    assert label.text == "Task title"
    print("Input label: PASS")

    # Submit the initially empty input and wait for visible error feedback.
    driver.find_element(By.ID, "add-task").click()
    error = wait.until(
        EC.visibility_of_element_located((By.ID, "error"))
    )
    assert error.text == "Enter a task title"

    # Confirm that the rejected submission did not add a list item.
    assert driver.find_elements(By.CSS_SELECTOR, "#tasks li") == []
    print("Empty-title validation: PASS")

    # Enter a valid title and activate the Add task button.
    title_input = driver.find_element(By.ID, "task-title")
    title_input.send_keys("Write README")
    driver.find_element(By.ID, "add-task").click()

    # Wait until the list contains exactly one task before inspecting it.
    wait.until(
        lambda browser: len(
            browser.find_elements(By.CSS_SELECTOR, "#tasks li")
        ) == 1
    )

    # Verify the displayed title and confirm that the form is ready
    # for another entry, with its input and previous error cleared.
    assert driver.find_element(By.CSS_SELECTOR, "#tasks li").text == (
        "Write README"
    )
    assert title_input.get_attribute("value") == ""
    assert driver.find_element(By.ID, "error").text == ""
    print("Add-task interaction: PASS")

finally:
    # End the browser session even if a check or interaction fails.
    driver.quit()