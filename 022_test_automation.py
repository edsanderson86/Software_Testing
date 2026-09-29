python -m pip install selenium

# browser_test.py
# Run with: python browser_test.py
# Requires Chrome installed on your computer.

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait


class PageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            title = "Home"
            heading = "Task Tracker"
            link = '<a id="next" href="/tasks">View tasks</a>'
        elif self.path == "/tasks":
            title = "Tasks"
            heading = "My Tasks"
            link = '<a href="/">Home</a>'
        else:
            self.send_error(404)
            return

        html = f"""<!doctype html>
<html>
<head><title>{title}</title></head>
<body><h1>{heading}</h1>{link}</body>
</html>""".encode()

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), PageHandler)
server_thread = Thread(target=server.serve_forever, daemon=True)
server_thread.start()
base_url = f"http://127.0.0.1:{server.server_port}"

driver = None

try:
    driver = webdriver.Chrome()

    # Browser management: window size and timeouts
    driver.set_window_size(900, 700)
    driver.set_page_load_timeout(10)

    # Navigation: open a page
    driver.get(base_url)
    assert driver.title == "Home"
    print("Page title:", driver.title)
    print("Current URL:", driver.current_url)
    print("Window size:", driver.get_window_size())

    # Get page information and interact with an element
    heading = driver.find_element(By.TAG_NAME, "h1")
    assert heading.text == "Task Tracker"
    print("Heading:", heading.text)
    print("Page contains a link:", 'id="next"' in driver.page_source)

    driver.find_element(By.ID, "next").click()
    assert driver.title == "Tasks"
    print("After click:", driver.current_url)

    # Navigation: back, forward, refresh
    driver.back()
    WebDriverWait(driver, 5).until(lambda browser: browser.title == "Home")

    driver.forward()
    WebDriverWait(driver, 5).until(lambda browser: browser.title == "Tasks")

    driver.refresh()
    assert driver.find_element(By.TAG_NAME, "h1").text == "My Tasks"
    print("Back, forward, and refresh: PASS")

    # Browser management: cookies
    driver.add_cookie({"name": "test_session", "value": "example"})
    assert driver.get_cookie("test_session")["value"] == "example"
    driver.delete_cookie("test_session")
    print("Add, read, and delete cookie: PASS")

    # close() closes one tab; quit() ends the whole browser session.
    driver.switch_to.new_window("tab")
    driver.get(base_url)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    print("Close extra tab: PASS")

finally:
    if driver is not None:
        driver.quit()
    server.shutdown()
    server.server_close()
    server_thread.join()
