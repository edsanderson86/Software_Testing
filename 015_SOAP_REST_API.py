# soap_and_rest_example.py
# Run with: python soap_and_rest_example.py

import json
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from urllib.request import Request, urlopen

TASKS = ["Write README", "Test the app"]
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
APP_NS = "urn:task-tracker"


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # REST: resource identified by a URL; response is JSON.
        if self.path != "/api/tasks":
            self.send_error(404)
            return

        body = json.dumps({"tasks": TASKS}).encode()
        self.respond(200, "application/json", body)

    def do_POST(self):
        # SOAP: XML message with an Envelope and Body.
        if self.path != "/soap":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        request_xml = self.rfile.read(length)

        try:
            envelope = ET.fromstring(request_xml)
            operation = envelope.find(
                f"./{{{SOAP_NS}}}Body/{{{APP_NS}}}GetTasks"
            )
            if operation is None:
                raise ValueError("Expected GetTasks operation")
        except (ET.ParseError, ValueError):
            self.send_error(400, "Invalid SOAP request")
            return

        response = ET.Element(f"{{{SOAP_NS}}}Envelope")
        body_element = ET.SubElement(response, f"{{{SOAP_NS}}}Body")
        result = ET.SubElement(body_element, f"{{{APP_NS}}}GetTasksResponse")

        for title in TASKS:
            ET.SubElement(result, f"{{{APP_NS}}}Task").text = title

        body = ET.tostring(response, encoding="utf-8", xml_declaration=True)
        self.respond(200, "text/xml; charset=utf-8", body)

    def respond(self, status, content_type, body):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), APIHandler)
thread = Thread(target=server.serve_forever, daemon=True)
thread.start()

base_url = f"http://127.0.0.1:{server.server_port}"

try:
    with urlopen(f"{base_url}/api/tasks") as response:
        print("REST response:", json.loads(response.read()))

    soap_request = f"""\
<soap:Envelope xmlns:soap="{SOAP_NS}" xmlns:app="{APP_NS}">
  <soap:Body>
    <app:GetTasks />
  </soap:Body>
</soap:Envelope>"""

    request = Request(
        f"{base_url}/soap",
        data=soap_request.encode(),
        headers={"Content-Type": "text/xml; charset=utf-8"},
        method="POST",
    )

    with urlopen(request) as response:
        print("SOAP response:", response.read().decode())
finally:
    server.shutdown()
    server.server_close()
    thread.join()