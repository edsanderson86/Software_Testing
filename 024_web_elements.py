# web_elements_example.py
# Install: python -m pip install selenium
# Run: python web_elements_example.py
# Requires Chrome installed on your computer.

from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

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

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

try:
    driver.get("data:text/html;charset=utf-8," + quote(html))

    # Dropdown
    dropdown = Select(driver.find_element(By.ID, "priority"))
    dropdown.select_by_visible_text("High")
    assert dropdown.first_selected_option.get_attribute("value") == "high"
    print("Dropdown: PASS")

    # Radio button
    work_radio = driver.find_element(
        By.CSS_SELECTOR, "input[name='task-type'][value='work']"
    )
    work_radio.click()
    assert work_radio.is_selected()
    print("Radio button: PASS")

    # Checkbox
    urgent_checkbox = driver.find_element(By.ID, "urgent")
    urgent_checkbox.click()
    assert urgent_checkbox.is_selected()
    print("Checkbox: PASS")

    # JavaScript alert
    driver.find_element(By.ID, "alert-button").click()
    alert = wait.until(EC.alert_is_present())
    assert alert.text == "Task saved"
    alert.accept()
    print("Alert: PASS")

    # Confirmation popup
    driver.find_element(By.ID, "confirm-button").click()
    confirmation = wait.until(EC.alert_is_present())
    confirmation.dismiss()
    assert driver.find_element(By.ID, "answer").text == "No"
    print("Confirmation: PASS")

    # Browser popup / new tab
    original_window = driver.current_window_handle
    driver.find_element(By.ID, "popup-button").click()
    wait.until(EC.number_of_windows_to_be(2))

    popup_window = next(
        handle for handle in driver.window_handles
        if handle != original_window
    )
    driver.switch_to.window(popup_window)
    assert driver.find_element(By.TAG_NAME, "h1").text == "Popup opened"
    driver.close()
    driver.switch_to.window(original_window)
    print("New window: PASS")

    # Dynamic element: wait until JavaScript adds it.
    wait.until(EC.element_to_be_clickable((By.ID, "load-button"))).click()
    result = wait.until(
        EC.visibility_of_element_located((By.ID, "dynamic-result"))
    )
    assert result.text == "Task loaded"
    print("Explicit wait for dynamic element: PASS")

finally:
    driver.quit()
``` 