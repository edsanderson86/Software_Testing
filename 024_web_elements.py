# web_elements_example.py
# Install: python -m pip install selenium
# Run: python web_elements_example.py
# Requires Chrome installed on your computer.
# Demonstrate form controls, dialogs, additional windows, and dynamic content.

from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Define a self-contained practice page with interactive controls.
# The controls demonstrate browser behaviour without saving or deleting tasks.
html = """
<!doctype html>
<html>
<head><title>Web Element Practice</title></head>
<body>
    <select id="priority">
        <option value="low">Low</option>
        <option value="high">High</option>
    </select>

    <label>
        <input type="radio" name="task-type" value="work">
        Work
    </label>
    <label>
        <input type="radio" name="task-type" value="personal">
        Personal
    </label>

    <label>
        <input type="checkbox" id="urgent">
        Urgent
    </label>

    <button id="alert-button" onclick="alert('Task saved')">
        Show alert
    </button>

    <button id="confirm-button"
            onclick="document.getElementById('answer').textContent =
                     confirm('Delete task?') ? 'Yes' : 'No'">
        Show confirmation
    </button>
    <p id="answer"></p>

    <button id="popup-button" onclick="
        const popup = window.open('', '_blank');
        popup.document.write('<title>Popup</title><h1>Popup opened</h1>');
        popup.document.close();
    ">Open popup</button>

    <button id="load-button" onclick="
        setTimeout(() => {
            const result = document.createElement('p');
            result.id = 'dynamic-result';
            result.textContent = 'Task loaded';
            document.body.appendChild(result);
        }, 800);
    ">Load task later</button>
</body>
</html>
"""

# Launch Chrome and allow up to five seconds for each explicit wait.
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

try:
    # Load the encoded HTML directly without starting a web server.
    driver.get("data:text/html;charset=utf-8," + quote(html))

    # Wrap the native select element with Selenium's dropdown helper.
    # Choose the visible label and verify the underlying option value.
    dropdown = Select(driver.find_element(By.ID, "priority"))
    dropdown.select_by_visible_text("High")
    assert dropdown.first_selected_option.get_attribute("value") == "high"
    print("Dropdown: PASS")

    # Identify the Work radio button by its group name and value.
    # Radio buttons with the same name form a single-choice group.
    work_radio = driver.find_element(
        By.CSS_SELECTOR, "input[name='task-type'][value='work']"
    )
    work_radio.click()
    assert work_radio.is_selected()
    print("Radio button: PASS")

    # Select the initially unchecked Urgent checkbox and verify its state.
    urgent_checkbox = driver.find_element(By.ID, "urgent")
    urgent_checkbox.click()
    assert urgent_checkbox.is_selected()
    print("Checkbox: PASS")

    # Open a JavaScript alert and wait until the dialog is available.
    # Verify its message, then accept it to dismiss the dialog.
    driver.find_element(By.ID, "alert-button").click()
    alert = wait.until(EC.alert_is_present())
    assert alert.text == "Task saved"
    alert.accept()
    print("Alert: PASS")

    # Open a confirmation dialog and dismiss it to simulate choosing Cancel.
    # The page records that choice as "No".
    driver.find_element(By.ID, "confirm-button").click()
    confirmation = wait.until(EC.alert_is_present())
    confirmation.dismiss()
    assert driver.find_element(By.ID, "answer").text == "No"
    print("Confirmation: PASS")

    # Remember the original window before opening another browsing context.
    # The browser may present the new context as a tab or a separate window.
    original_window = driver.current_window_handle
    driver.find_element(By.ID, "popup-button").click()
    wait.until(EC.number_of_windows_to_be(2))

    # Identify the new window by finding the handle that differs from the original.
    popup_window = next(
        handle for handle in driver.window_handles
        if handle != original_window
    )

    # Switch to the new context and wait for its heading to become visible.
    driver.switch_to.window(popup_window)
    popup_heading = wait.until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))
    )
    assert popup_heading.text == "Popup opened"

    # Close the popup and restore focus to the original page.
    driver.close()
    driver.switch_to.window(original_window)
    print("New window: PASS")

    # Click the load button once it is visible and enabled.
    # Its JavaScript inserts a result element after an 800-millisecond delay.
    wait.until(EC.element_to_be_clickable((By.ID, "load-button"))).click()

    # Wait for the inserted element to become visible rather than using
    # a fixed sleep that might be too short or unnecessarily long.
    result = wait.until(
        EC.visibility_of_element_located((By.ID, "dynamic-result"))
    )
    assert result.text == "Task loaded"
    print("Explicit wait for dynamic element: PASS")

finally:
    # End the browser session even if an interaction or assertion fails.
    driver.quit()