# browser_test.py
# Install the dependency: python -m pip install selenium
# Run with: python browser_test.py
# Requires Chrome installed on your computer.
# Demonstrate browser navigation, element interaction, cookies, and tabs
# against a small local website.

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class PageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Provide two linked pages so navigation can be tested locally.
        if self.path == "/":
            title = "Home"
            heading = "Task Tracker"
            link = '<a id="next" href="/tasks">View tasks</a>'
        elif self.path == "/tasks":
            title = "Tasks"
            heading = "My Tasks"
            link = '<a href="/">Home</a>'
        else:
            # Return a not-found response for unsupported paths.
            self.send_error(404)
            return

        # Build the selected page and encode it for transmission.
        html = f"""<!doctype html>
<html>
<head><title>{title}</title></head>
<body><h1>{heading}</h1>{link}</body>
</html>""".encode()

        # Describe the response body before sending its bytes.
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def log_message(self, format, *args):
        # Suppress request logs to keep the test output readable.
        pass


# Start the website on a local port chosen by the operating system.
server = ThreadingHTTPServer(("127.0.0.1", 0), PageHandler)
server_thread = Thread(target=server.serve_forever, daemon=True)
server_thread.start()
base_url = f"http://127.0.0.1:{server.server_port}"

# Allow cleanup to run even if browser initialization fails.
driver = None

try:
    # Launch a Chrome browser session controlled by Selenium.
    driver = webdriver.Chrome()

    # Set consistent window dimensions and a page-loading timeout.
    driver.set_window_size(900, 700)
    driver.set_page_load_timeout(10)

    # Open the home page and check its title.
    driver.get(base_url)
    assert driver.title == "Home"
    print("Page title:", driver.title)
    print("Current URL:", driver.current_url)
    print("Window size:", driver.get_window_size())

    # Locate the main heading by its HTML tag and verify its visible text.
    heading = driver.find_element(By.TAG_NAME, "h1")
    assert heading.text == "Task Tracker"
    print("Heading:", heading.text)

    # Inspect the page source for the expected link identifier.
    # This prints an observation rather than asserting that the link exists.
    print("Page contains a link:", 'id="next"' in driver.page_source)

    # Locate the navigation link by ID and follow it to the tasks page.
    driver.find_element(By.ID, "next").click()
    assert driver.title == "Tasks"
    print("After click:", driver.current_url)

    # Return to the previous page and wait for its expected title.
    driver.back()
    WebDriverWait(driver, 5).until(lambda browser: browser.title == "Home")

    # Move forward through browser history and verify the destination.
    driver.forward()
    WebDriverWait(driver, 5).until(lambda browser: browser.title == "Tasks")

    # Reload the current page and confirm that its heading remains correct.
    driver.refresh()
    assert driver.find_element(By.TAG_NAME, "h1").text == "My Tasks"
    print("Back, forward, and refresh: PASS")

    # Add a sample cookie for the current site and verify its stored value.
    driver.add_cookie({"name": "test_session", "value": "example"})
    assert driver.get_cookie("test_session")["value"] == "example"

    # Delete the sample cookie after checking it.
    # This example calls deletion without separately verifying its absence.
    driver.delete_cookie("test_session")
    print("Add, read, and delete cookie: PASS")

    # Open an additional tab and load the home page.
    driver.switch_to.new_window("tab")
    driver.get(base_url)

    # Close only the active tab, then switch back to the remaining tab.
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print("Close extra tab: PASS")

finally:
    # End the entire browser session if it was successfully created.
    # Use a nested finally so server cleanup runs even if quit() raises.
    try:
        if driver is not None:
            driver.quit()
    finally:
        # Stop the local website, release its socket, and join its thread.
        server.shutdown()
        server.server_close()
        server_thread.join()
