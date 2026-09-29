# element_locators.py
# Install: python -m pip install selenium
# Run: python element_locators.py
# Requires Chrome installed on your computer.

from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By

html = """
<!doctype html>
<html>
<head><title>Locator Practice</title></head>
<body>
    <h1>Task Tracker</h1>
    <input id="task-title" name="title" class="task-input"
           placeholder="New task">
    <button class="add-button">Add task</button>
    <a href="#tasks">View all tasks</a>
    <ul id="tasks">
        <li class="task-item">Write README</li>
        <li class="task-item">Test the app</li>
    </ul>
</body>
</html>
"""

driver = webdriver.Chrome()

try:
    driver.get("data:text/html;charset=utf-8," + quote(html))

    # ID
    title_input = driver.find_element(By.ID, "task-title")
    print("ID:", title_input.get_attribute("placeholder"))

    # Name
    print("Name:", driver.find_element(By.NAME, "title").get_attribute("id"))

    # Class name
    print("Class name:", driver.find_element(By.CLASS_NAME, "add-button").text)

    # Tag name
    print("Tag name:", driver.find_element(By.TAG_NAME, "h1").text)

    # Exact link text
    print("Link text:", driver.find_element(By.LINK_TEXT, "View all tasks").text)

    # Partial link text
    print(
        "Partial link text:",
        driver.find_element(By.PARTIAL_LINK_TEXT, "all tasks").text,
    )

    # CSS selector
    print(
        "CSS selector:",
        driver.find_element(By.CSS_SELECTOR, "#tasks .task-item").text,
    )

    # XPath
    print(
        "XPath:",
        driver.find_element(
            By.XPATH, "//li[contains(@class, 'task-item')][2]"
        ).text,
    )

    # find_elements returns every match.
    tasks = driver.find_elements(By.CSS_SELECTOR, "li.task-item")
    assert len(tasks) == 2
    print("All tasks:", [task.text for task in tasks])

finally:
    driver.quit()