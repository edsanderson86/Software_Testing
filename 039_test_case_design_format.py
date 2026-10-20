# test_case_design_format.py
# Run with: python test_case_design_format.py
# Present a structured test case with setup, inputs, actions, and outcomes.
# This script prints the specification; it does not execute a booking.

from dataclasses import dataclass, field


# Pair each action with the observable result expected immediately afterward.
@dataclass
class TestStep:
    action: str
    expected_result: str


# Separate test design details from fields populated during execution.
@dataclass
class TestCase:
    id: str
    title: str
    requirement_id: str
    feature: str
    priority: str
    test_type: str
    preconditions: list[str]
    test_data: dict[str, str]
    steps: list[TestStep]
    postconditions: list[str]

    # Leave execution details unset until a tester records evidence.
    # Status is descriptive text; this model does not validate its value.
    actual_result: str = ""
    status: str = "Not Run"
    defect_id: str = ""
    notes: str = ""


# Design a boundary test for the transition from one available seat to zero.
# The requirement ID links the case to the behaviour it is intended to verify.
test_case = TestCase(
    id="FB-003",
    title="Book the last available seat",
    requirement_id="REQ-BOOK-01",
    feature="Flight booking",
    priority="High",
    test_type="Functional / Boundary",

    # Establish these conditions before carrying out the test steps.
    preconditions=[
        "The user is signed in.",
        "Flight 101 has exactly one available seat.",
    ],

    # Supply explicit values so the actions can be repeated consistently.
    test_data={
        "flight_id": "101",
        "passenger_name": "Alex Smith",
    },

    # Describe the workflow in order, with an expected result for each action.
    steps=[
        TestStep(
            action="Search for flight 101.",
            expected_result="Flight 101 appears with one seat available.",
        ),
        TestStep(
            action="Select flight 101 and enter Alex Smith.",
            expected_result="The passenger details are accepted.",
        ),
        TestStep(
            action="Confirm the booking.",
            expected_result="A booking reference is displayed.",
        ),
    ],

    # Define the stored state to verify after completing the workflow.
    postconditions=[
        "One confirmed booking exists.",
        "Flight 101 has zero available seats.",
    ],
)


def print_test_case(case: TestCase) -> None:
    # Display identifying information and the test's classification.
    print(f"TEST CASE: {case.id}")
    print(f"Title: {case.title}")
    print(f"Requirement: {case.requirement_id}")
    print(f"Feature: {case.feature}")
    print(f"Priority: {case.priority}")
    print(f"Type: {case.test_type}")

    # Show the required starting conditions.
    print("\nPreconditions:")
    for item in case.preconditions:
        print(f"- {item}")

    # List the inputs needed to perform the test.
    print("\nTest data:")
    for name, value in case.test_data.items():
        print(f"- {name}: {value}")

    # Number actions and keep each expected result beside its action.
    print("\nSteps:")
    for number, step in enumerate(case.steps, start=1):
        print(f"{number}. Action: {step.action}")
        print(f"   Expected: {step.expected_result}")

    # Show the final conditions that require verification.
    print("\nPostconditions:")
    for item in case.postconditions:
        print(f"- {item}")

    # Use readable placeholders for execution fields that remain empty.
    # These values are displayed as supplied, without checking consistency.
    print(f"\nActual result: {case.actual_result or 'Pending'}")
    print(f"Status: {case.status}")
    print(f"Defect ID: {case.defect_id or 'None'}")
    print(f"Notes: {case.notes or 'None'}")


# Print the designed case with its initial Not Run status.
print_test_case(test_case)