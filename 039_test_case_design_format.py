# test_case_design_format.py
# Run with: python test_case_design_format.py

from dataclasses import dataclass, field


@dataclass
class TestStep:
    action: str
    expected_result: str


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
    actual_result: str = ""
    status: str = "Not Run"
    defect_id: str = ""
    notes: str = ""


test_case = TestCase(
    id="FB-003",
    title="Book the last available seat",
    requirement_id="REQ-BOOK-01",
    feature="Flight booking",
    priority="High",
    test_type="Functional / Boundary",
    preconditions=[
        "The user is signed in.",
        "Flight 101 has exactly one available seat.",
    ],
    test_data={
        "flight_id": "101",
        "passenger_name": "Alex Smith",
    },
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
    postconditions=[
        "One confirmed booking exists.",
        "Flight 101 has zero available seats.",
    ],
)


def print_test_case(case: TestCase) -> None:
    print(f"TEST CASE: {case.id}")
    print(f"Title: {case.title}")
    print(f"Requirement: {case.requirement_id}")
    print(f"Feature: {case.feature}")
    print(f"Priority: {case.priority}")
    print(f"Type: {case.test_type}")

    print("\nPreconditions:")
    for item in case.preconditions:
        print(f"- {item}")

    print("\nTest data:")
    for name, value in case.test_data.items():
        print(f"- {name}: {value}")

    print("\nSteps:")
    for number, step in enumerate(case.steps, start=1):
        print(f"{number}. Action: {step.action}")
        print(f"   Expected: {step.expected_result}")

    print("\nPostconditions:")
    for item in case.postconditions:
        print(f"- {item}")

    print(f"\nActual result: {case.actual_result or 'Pending'}")
    print(f"Status: {case.status}")
    print(f"Defect ID: {case.defect_id or 'None'}")
    print(f"Notes: {case.notes or 'None'}")


print_test_case(test_case)