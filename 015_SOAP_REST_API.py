# soap_and_rest_example.py
# Run with: python soap_and_rest_example.py
# Demonstrate two ways to retrieve the same task list over HTTP:
# a REST-style endpoint returning JSON and a SOAP endpoint returning XML.

import json
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen

# Both endpoints use the same sample data.
TASKS = ["Write README", "Test the app"]

# Namespaces identify SOAP envelope elements and application elements.
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
APP_NS = "urn:task-tracker"


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Retrieve the tasks resource through its URL.
        if self.path != "/api/tasks":
            self.send_error(404)
            return

        # Serialize the task list as JSON and encode it for transmission.
        body = json.dumps({"tasks": TASKS}).encode()
        self.respond(200, "application/json", body)

    def do_POST(self):
        # Accept SOAP operation requests at a dedicated endpoint.
        if self.path != "/soap":
            self.send_error(404)
            return

        # Read the number of request-body bytes specified by the client.
        length = int(self.headers.get("Content-Length", "0"))
        request_xml = self.rfile.read(length)

        try:
            # Parse the XML and look for GetTasks inside the SOAP Body.
            envelope = ET.fromstring(request_xml)
            operation = envelope.find(
                f"./{{{SOAP_NS}}}Body/{{{APP_NS}}}GetTasks"
            )
            if operation is None:
                raise ValueError("Expected GetTasks operation")
        except (ET.ParseError, ValueError):
            # This simplified example returns an HTTP error for invalid input.
            self.send_error(400, "Invalid SOAP request")
            return

        # Build an XML response containing an Envelope, Body, and result.
        response = ET.Element(f"{{{SOAP_NS}}}Envelope")
        body_element = ET.SubElement(response, f"{{{SOAP_NS}}}Body")
        result = ET.SubElement(body_element, f"{{{APP_NS}}}GetTasksResponse")

        # Include each task title as a separate application element.
        for title in TASKS:
            ET.SubElement(result, f"{{{APP_NS}}}Task").text = title

        # Serialize the XML tree into UTF-8 bytes with an XML declaration.
        body = ET.tostring(response, encoding="utf-8", xml_declaration=True)
        self.respond(200, "text/xml; charset=utf-8", body)

    def respond(self, status, content_type, body):
        # Share response-writing logic between the two endpoints.
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        # Suppress request logs so the example output shows only results.
        pass


# Start a local server on an available port chosen by the operating system.
server = ThreadingHTTPServer(("127.0.0.1", 0), APIHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()

base_url = f"http://127.0.0.1:{server.server_port}"

try:
    # Retrieve the REST-style response and decode JSON into Python data.
    with urlopen(f"{base_url}/api/tasks") as response:
        print("REST response:", json.loads(response.read()))

    # Specify the requested SOAP operation within an XML envelope.
    soap_request = f"""\
<soap:Envelope xmlns:soap="{SOAP_NS}" xmlns:app="{APP_NS}">
  <soap:Body>
    <app:GetTasks />
  </soap:Body>
</soap:Envelope>"""

    # Send the SOAP XML as the body of an HTTP POST request.
    request = Request(
        f"{base_url}/soap",
        data=soap_request.encode(),
        headers={"Content-Type": "text/xml; charset=utf-8"},
        method="POST",
    )

    # Display the returned SOAP XML as text.
    with urlopen(request) as response:
        print("SOAP response:", response.read().decode())
finally:
    # Release the server socket and wait for its background thread to stop.
    server.shutdown()
    server.server_close()
    thread.join()