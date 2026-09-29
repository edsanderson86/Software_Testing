# user_interface_testing.py
# Install: python -m pip install selenium
# Run: python user_interface_testing.py
# Requires Chrome installed on your computer.

from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

try:
    driver.get("data:text/html;charset=utf-8," + quote(html))

    # Page content and visible controls
    assert driver.title == "To-Do List"
    assert driver.find_element(By.TAG_NAME, "h1").text == "To-Do List"
    assert driver.find_element(By.ID, "task-title").is_displayed()
    assert driver.find_element(By.ID, "add-task").is_enabled()
    print("Page content and controls: PASS")

    # Accessibility: the input has an associated label
    label = driver.find_element(By.CSS_SELECTOR, "label[for='task-title']")
    assert label.text == "Task title"
    print("Input label: PASS")

    # Validation: empty input shows an error
    driver.find_element(By.ID, "add-task").click()
    error = wait.until(
        EC.visibility_of_element_located((By.ID, "error"))
    )
    assert error.text == "Enter a task title"
    assert driver.find_elements(By.CSS_SELECTOR, "#tasks li") == []
    print("Empty-title validation: PASS")

    # Happy path: adding a task updates the interface
    title_input = driver.find_element(By.ID, "task-title")
    title_input.send_keys("Write README")
    driver.find_element(By.ID, "add-task").click()

    wait.until(
        lambda browser: len(
            browser.find_elements(By.CSS_SELECTOR, "#tasks li")
        ) == 1
    )

    assert driver.find_element(By.CSS_SELECTOR, "#tasks li").text == (
        "Write README"
    )
    assert title_input.get_attribute("value") == ""
    assert driver.find_element(By.ID, "error").text == ""
    print("Add-task interaction: PASS")

finally:
    driver.quit()