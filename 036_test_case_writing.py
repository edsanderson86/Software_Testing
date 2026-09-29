# test_case_writing.py
# Run with: python test_case_writing.py

from dataclasses import dataclass


class TodoList:
    def __init__(self):
        self.tasks = []

    def add(self, title):
        title = title.strip()
        if not title:
            raise ValueError("A task title is required")
        self.tasks.append({"title": title, "completed": False})

    def complete(self, position):
        self.tasks[position - 1]["completed"] = True


@dataclass
class TestCase:
    id: str
    title: str
    requirement: str
    precondition: str
    test_data: str
    steps: list[str]
    expected_result: str
    execute: callable


def test_add_valid_task():
    app = TodoList()
    app.add("Write README")
    assert app.tasks == [
        {"title": "Write README", "completed": False}
    ]


def test_reject_blank_title():
    app = TodoList()

    try:
        app.add("   ")
    except ValueError as error:
        assert str(error) == "A task title is required"
    else:
        raise AssertionError("Blank title was accepted")

    assert app.tasks == []


def test_complete_task():
    app = TodoList()
    app.add("Test the app")
    app.complete(1)
    assert app.tasks[0]["completed"] is True


test_cases = [
    TestCase(
        id="TC-001",
        title="Add a valid task",
        requirement="REQ-001",
        precondition="The to-do list is empty.",
        test_data='Title: "Write README"',
        steps=[
            "Open the to-do list.",
            'Enter "Write README".',
            "Select Add.",
        ],
        expected_result="The task appears with completed set to False.",
        execute=test_add_valid_task,
    ),
    TestCase(
        id="TC-002",
        title="Reject a blank task title",
        requirement="REQ-001",
        precondition="The to-do list is empty.",
        test_data="Title: three spaces",
        steps=[
            "Open the to-do list.",
            "Enter three spaces.",
            "Select Add.",
        ],
        expected_result="An error appears and no task is added.",
        execute=test_reject_blank_title,
    ),
    TestCase(
        id="TC-003",
        title="Complete an existing task",
        requirement="REQ-002",
        precondition='A task named "Test the app" exists.',
        test_data="Task position: 1",
        steps=[
            'Find the "Test the app" task.',
            "Select Complete.",
        ],
        expected_result="The task is marked complete.",
        execute=test_complete_task,
    ),
]


for case in test_cases:
    print(f"\n{case.id}: {case.title}")
    print("Requirement:", case.requirement)
    print("Precondition:", case.precondition)
    print("Test data:", case.test_data)

    for number, step in enumerate(case.steps, start=1):
        print(f"Step {number}: {step}")

    print("Expected:", case.expected_result)

    try:
        case.execute()
    except Exception as error:
        print(f"Actual: {type(error).__name__}: {error}")
        print("Result: FAIL")
    else:
        print("Actual: Expected behavior observed")
        print("Result: PASS")