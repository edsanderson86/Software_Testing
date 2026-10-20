# test_case_writing.py
# Run with: python test_case_writing.py
# Pair structured test-case descriptions with executable checks.
# Written steps describe user actions; the checks exercise Python methods.

from dataclasses import dataclass


class TodoList:
    def __init__(self):
        # Start each instance with an independent, empty task list.
        self.tasks = []

    def add(self, title):
        # Clean the title and reject blank input before changing the list.
        title = title.strip()
        if not title:
            raise ValueError("A task title is required")

        # Store valid tasks as incomplete.
        self.tasks.append({"title": title, "completed": False})

    def complete(self, position):
        # Convert a displayed position to Python's zero-based index.
        # This example assumes a valid position; zero would select the last task.
        self.tasks[position - 1]["completed"] = True


# Keep the requirement, setup, inputs, steps, and expected outcome together.
# The execute field holds the function used to verify the test case.
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
    # Establish the empty-list precondition.
    app = TodoList()

    # Add the specified title and verify the complete stored record.
    app.add("Write README")
    assert app.tasks == [
        {"title": "Write README", "completed": False}
    ]


def test_reject_blank_title():
    # Use a fresh instance so other test cases cannot affect this check.
    app = TodoList()

    try:
        # Submit the whitespace-only input described in the test data.
        app.add("   ")
    except ValueError as error:
        # Verify the validation message as well as the exception type.
        assert str(error) == "A task title is required"
    else:
        raise AssertionError("Blank title was accepted")

    # Confirm that rejecting the input left the list empty.
    assert app.tasks == []


def test_complete_task():
    # Create the task required by this test's precondition.
    app = TodoList()
    app.add("Test the app")

    # Complete the first task and verify its updated status.
    app.complete(1)
    assert app.tasks[0]["completed"] is True


# Define readable test cases and associate each with its verification function.
# Function references are stored here; execution happens in the reporting loop.
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


# Present each test's context before running its associated check.
for case in test_cases:
    print(f"\n{case.id}: {case.title}")
    print("Requirement:", case.requirement)
    print("Precondition:", case.precondition)
    print("Test data:", case.test_data)

    # Number the written steps from 1 for easy reference.
    for number, step in enumerate(case.steps, start=1):
        print(f"Step {number}: {step}")

    print("Expected:", case.expected_result)

    try:
        case.execute()
    except Exception as error:
        # Report assertion failures or other exceptions, then continue
        # with the remaining cases. Failures do not set a nonzero exit code.
        print(f"Actual: {type(error).__name__}: {error}")
        print("Result: FAIL")
    else:
        # Report success when the verification function raises no exception.
        print("Actual: Expected behavior observed")
        print("Result: PASS")