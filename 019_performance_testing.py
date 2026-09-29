# performance_test.py
# Run with: python performance_test.py
#
# Local demonstration:
# - Closed load: each virtual user waits before its next iteration.
# - Open load: requests start at a fixed rate.
# - Parameterization: each request gets a unique task title.
# - Correlation: login token and task ID come from earlier responses.
# - Timer and think time: measure responses; pause between user actions.
# - Metrics: response time, throughput, utilization, and error rate.

import json
import math
import statistics
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock, Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

tasks = {}
task_lock = Lock()
server_busy_seconds = 0.0
busy_lock = Lock()


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        global server_busy_seconds
        started = time.perf_counter()

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length) or b"{}")

            if self.path == "/login":
                self.respond(200, {"token": "test-token"})
                return

            if self.path == "/tasks":
                if self.headers.get("Authorization") != "Bearer test-token":
                    self.respond(401, {"error": "Unauthorized"})
                    return

                title = data.get("title", "").strip()
                if not title:
                    self.respond(400, {"error": "Title required"})
                    return

                time.sleep(0.02)  # Simulated server work
                task_id = uuid.uuid4().hex

                with task_lock:
                    tasks[task_id] = title

                self.respond(201, {"id": task_id, "title": title})
                return

            self.respond(404, {"error": "Not found"})
        finally:
            with busy_lock:
                server_busy_seconds += time.perf_counter() - started

    def do_GET(self):
        global server_busy_seconds
        started = time.perf_counter()

        try:
            if self.headers.get("Authorization") != "Bearer test-token":
                self.respond(401, {"error": "Unauthorized"})
                return

            task_id = self.path.removeprefix("/tasks/")
            with task_lock:
                title = tasks.get(task_id)

            if title is None:
                self.respond(404, {"error": "Task not found"})
            else:
                time.sleep(0.01)
                self.respond(200, {"id": task_id, "title": title})
        finally:
            with busy_lock:
                server_busy_seconds += time.perf_counter() - started

    def respond(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
server_thread = Thread(target=server.serve_forever, daemon=True)
server_thread.start()
base_url = f"http://127.0.0.1:{server.server_port}"


def timed_request(method, path, payload=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(
        base_url + path,
        data=json.dumps(payload).encode() if payload is not None else None,
        headers=headers,
        method=method,
    )

    started = time.perf_counter()
    try:
        response = urlopen(request, timeout=5)
    except HTTPError as error:
        response = error

    with response:
        result = {
            "status": response.status,
            "body": json.loads(response.read()),
            "latency_ms": (time.perf_counter() - started) * 1000,
        }

    return result


def user_iteration(user_number, iteration_number, think_time_seconds=0.05):
    measurements = []

    login = timed_request("POST", "/login", {"user": user_number})
    measurements.append(login)
    if login["status"] != 200:
        return measurements

    token = login["body"]["token"]  # Correlation: extract token

    time.sleep(think_time_seconds)  # Timer: simulated user think time

    title = f"User {user_number} task {iteration_number}-{uuid.uuid4().hex[:6]}"
    created = timed_request("POST", "/tasks", {"title": title}, token)
    measurements.append(created)
    if created["status"] != 201:
        return measurements

    task_id = created["body"]["id"]  # Correlation: extract task ID

    time.sleep(think_time_seconds)

    retrieved = timed_request("GET", f"/tasks/{task_id}", token=token)
    measurements.append(retrieved)

    # Assertions check correctness, not just HTTP speed.
    assert retrieved["status"] == 200
    assert retrieved["body"]["title"] == title

    return measurements


def closed_load(users=5, iterations_per_user=4):
    def virtual_user(user_number):
        results = []
        for iteration in range(iterations_per_user):
            results.extend(user_iteration(user_number, iteration))
        return results

    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=users) as pool:
        futures = [pool.submit(virtual_user, user) for user in range(users)]
        results = [item for future in as_completed(futures) for item in future.result()]

    return results, time.perf_counter() - started


def open_load(rate_per_second=5, duration_seconds=3, max_workers=20):
    started = time.perf_counter()
    futures = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        count = math.ceil(rate_per_second * duration_seconds)

        for index in range(count):
            target_time = started + index / rate_per_second
            time.sleep(max(0, target_time - time.perf_counter()))
            futures.append(pool.submit(user_iteration, index, 0))

        results = [item for future in as_completed(futures) for item in future.result()]

    return results, time.perf_counter() - started


def percentile(values, percent):
    ordered = sorted(values)
    position = (len(ordered) - 1) * percent / 100
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def report(name, results, elapsed, busy_before):
    latencies = [result["latency_ms"] for result in results]
    failures = sum(result["status"] >= 400 for result in results)
    busy_delta = server_busy_seconds - busy_before

    print(f"\n{name}")
    print(f"Requests:           {len(results)}")
    print(f"Elapsed:            {elapsed:.2f} s")
    print(f"Throughput:         {len(results) / elapsed:.2f} requests/s")
    print(f"Error rate:         {failures / len(results) * 100:.1f}%")
    print(f"Mean (average):     {statistics.mean(latencies):.2f} ms")
    print(f"Median:             {statistics.median(latencies):.2f} ms")
    print(f"90th percentile:    {percentile(latencies, 90):.2f} ms")
    print(f"95th percentile:    {percentile(latencies, 95):.2f} ms")
    print(f"Standard deviation:{statistics.pstdev(latencies):.2f} ms")
    print(f"Server busy time:   {busy_delta:.2f} cumulative seconds")
    print(
        "Busy-equivalent workers: "
        f"{busy_delta / elapsed:.2f}"
    )  # Not CPU utilization; handlers can overlap and sleep.


try:
    before = server_busy_seconds
    results, elapsed = closed_load()
    report("CLOSED LOAD PROFILE", results, elapsed, before)

    before = server_busy_seconds
    results, elapsed = open_load()
    report("OPEN LOAD PROFILE", results, elapsed, before)
finally:
    server.shutdown()
    server.server_close()
    server_thread.join()