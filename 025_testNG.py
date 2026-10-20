# frames_windows_screenshots.py
# Install: python -m pip install selenium
# Run: python frames_windows_screenshots.py
# Requires Chrome installed on your computer.
# Demonstrate iframe interaction, window switching, and screenshot capture.

from pathlib import Path
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# Define a main page containing an embedded document and a help-window button.
# The iframe's srcdoc attribute supplies its HTML without a separate server.
# The Save button is illustrative and has no task-saving behaviour.
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

# Start Chrome and configure explicit waits of up to five seconds.
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 5)

try:
    # Load the practice page directly from an encoded HTML string.
    driver.get("data:text/html;charset=utf-8," + quote(html))

    # Save the original window handle so it can be selected again later.
    original_window = driver.current_window_handle

    # Wait for the iframe and switch Selenium's context into its document.
    # Elements inside the iframe must be located from this context.
    wait.until(
        EC.frame_to_be_available_and_switch_to_it((By.ID, "task-frame"))
    )

    # Enter a task title and confirm the input holds the expected value.
    title_input = wait.until(
        EC.visibility_of_element_located((By.ID, "task-title"))
    )
    title_input.send_keys("Write README")
    assert title_input.get_attribute("value") == "Write README"

    # Leave the iframe before locating elements in the main document.
    driver.switch_to.default_content()
    assert driver.find_element(By.TAG_NAME, "h1").text == "Main page"
    print("Iframe interaction: PASS")

    # Open the help context, which may appear as a tab or separate window.
    driver.find_element(By.ID, "open-window").click()
    wait.until(EC.number_of_windows_to_be(2))

    # Identify the new context by excluding the original window handle.
    help_window = next(
        handle for handle in driver.window_handles
        if handle != original_window
    )
    driver.switch_to.window(help_window)

    # Wait until the popup has populated its title before checking it.
    wait.until(EC.title_is("Task Help"))
    assert driver.title == "Task Help"
    print("Window switching: PASS")

    # Close only the help context and return to the original page.
    driver.close()
    driver.switch_to.window(original_window)

    # Capture the current viewport as a PNG in the working directory.
    # Saving to the same filename replaces an existing screenshot.
    screenshot = Path("automation_screenshot.png")
    saved = driver.save_screenshot(str(screenshot))
    assert saved
    print(f"Screenshot saved: {screenshot.resolve()}")

finally:
    # Close all remaining browser windows and release the driver session.
    driver.quit()