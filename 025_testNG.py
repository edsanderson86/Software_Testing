# frames_windows_screenshots.py
# Install: python -m pip install selenium
# Run: python frames_windows_screenshots.py
# Requires Chrome installed on your computer.

from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

html = """
<!doctype html>
<html>
<head><title>Frames and Windows</title></head>
<body>
    <h1>Main page</h1>

    <iframe id="task-frame" srcdoc="
        <html>
        <body>
            <input id='task-title' placeholder='Enter a task'>
            <button id='save'>Save</button>
        </body>
        </html>
    "></iframe>

    <button id="open-window" onclick="
        const popup = window.open('', '_blank');
        popup.document.write('<title>Task Help</title><h1>Help window</h1>');
        popup.document.close();
    ">Open help</button>
</body>
</html>
"""

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

try:
    driver.get("data:text/html;charset=utf-8," + quote(html))
    original_window = driver.current_window_handle

    # Switch into an iframe to interact with its elements.
    wait.until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "task-frame"))
    )

    title_input = wait.until(
        EC.visibility_of_element_located((By.ID, "task-title"))
    )
    title_input.send_keys("Write README")
    assert title_input.get_attribute("value") == "Write README"

    # Return to the main document.
    driver.switch_to.default_content()
    assert driver.find_element(By.TAG_NAME, "h1").text == "Main page"
    print("Iframe interaction: PASS")

    # Open and switch to a separate browser window.
    driver.find_element(By.ID, "open-window").click()
    wait.until(EC.number_of_windows_to_be(2))

    help_window = next(
        handle for handle in driver.window_handles
        if handle != original_window
    )
    driver.switch_to.window(help_window)
    assert driver.title == "Task Help"
    print("Window switching: PASS")

    driver.close()
    driver.switch_to.window(original_window)

    # Save evidence of the final browser state.
    screenshot = Path("automation_screenshot.png")
    assert driver.save_screenshot(str(screenshot))
    print(f"Screenshot saved: {screenshot.resolve()}")

finally:
    driver.quit()