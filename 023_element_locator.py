# element_locators.py
# Install: python -m pip install selenium
# Run: python element_locators.py
# Requires Chrome installed on your computer.
# Demonstrate different ways to locate elements on a sample page.

from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By

# Provide a self-contained page with attributes and text for locator practice.
# The button is a sample element and does not add tasks.
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

# Launch Chrome for the demonstration.
driver = webdriver.Chrome()

try:
    # Encode the HTML in a data URL to load it without a web server.
    driver.get("data:text/html;charset=utf-8," + quote(html))

    # Locate the input by its ID and read its placeholder attribute.
    title_input = driver.find_element(By.ID, "task-title")
    print("ID:", title_input.get_attribute("placeholder"))

    # Locate the same input through its name attribute.
    print("Name:", driver.find_element(By.NAME, "title").get_attribute("id"))

    # Match the button using a single class name.
    print("Class name:", driver.find_element(By.CLASS_NAME, "add-button").text)

    # Locate the first h1 element and read its visible text.
    print("Tag name:", driver.find_element(By.TAG_NAME, "h1").text)

    # Match an anchor using its complete visible link text.
    print("Link text:", driver.find_element(By.LINK_TEXT, "View all tasks").text)

    # Match the same anchor using part of its visible link text.
    print(
        "Partial link text:",
        driver.find_element(By.PARTIAL_LINK_TEXT, "all tasks").text,
    )

    # Combine an ID and a class selector to find a task inside the list.
    # find_element returns the first matching element.
    print(
        "CSS selector:",
        driver.find_element(By.CSS_SELECTOR, "#tasks .task-item").text,
    )

    # Use XPath to select the second matching list item among its siblings.
    # XPath positions start at 1, so [2] identifies the second item here.
    print(
        "XPath:",
        driver.find_element(
            By.XPATH, "//li[contains(@class, 'task-item')][2]"
        ).text,
    )

    # Collect every matching task element.
    # find_elements returns an empty list when nothing matches,
    # whereas find_element raises an exception if no match is found.
    tasks = driver.find_elements(By.CSS_SELECTOR, "li.task-item")

    # Verify the number of tasks, then display their visible titles.
    assert len(tasks) == 2
    print("All tasks:", [task.text for task in tasks])

finally:
    # Close all browser windows and release the driver session.
    driver.quit()