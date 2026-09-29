# flight_booking_test_design.py
# Run with: python flight_booking_test_design.py

from dataclasses import dataclass


@dataclass
class TestCase:
    id: str
    feature: str
    title: str
    priority: str
    precondition: str
    steps: list[str]
    expected_result: str


test_cases = [
    TestCase(
        "FB-001",
        "Search",
        "Find available flights",
        "High",
        "A London-to-Paris flight has available seats.",
        [
            "Enter London as origin.",
            "Enter Paris as destination.",
            "Select Search.",
        ],
        "The matching flight appears with its departure time and seats.",
    ),
    TestCase(
        "FB-002",
        "Search",
        "No matching flights",
        "Medium",
        "No flights exist for the selected route.",
        [
            "Enter an origin and destination with no flights.",
            "Select Search.",
        ],
        "A clear no-results message appears.",
    ),
    TestCase(
        "FB-003",
        "Booking",
        "Book the last available seat",
        "High",
        "A flight has exactly one seat left.",
        [
            "Select the flight.",
            "Enter a valid passenger name.",
            "Confirm the booking.",
        ],
        "One booking is created and available seats becomes zero.",
    ),
    TestCase(
        "FB-004",
        "Booking",
        "Reject booking when flight is full",
        "High",
        "A flight has zero seats left.",
        [
            "Select the full flight.",
            "Attempt to confirm a booking.",
        ],
        "No booking is created and the seat count remains zero.",
    ),
    TestCase(
        "FB-005",
        "Booking",
        "Reject a blank passenger name",
        "Medium",
        "A flight has available seats.",
        [
            "Select the flight.",
            "Enter spaces as the passenger name.",
            "Confirm the booking.",
        ],
        "A validation message appears; no seat is taken.",
    ),
    TestCase(
        "FB-006",
        "Cancellation",
        "Cancel a confirmed booking",
        "High",
        "A confirmed booking exists.",
        [
            "Open the booking.",
            "Select Cancel.",
            "Confirm cancellation.",
        ],
        "Booking status becomes cancelled and one seat is restored.",
    ),
    TestCase(
        "FB-007",
        "Cancellation",
        "Prevent cancelling twice",
        "Medium",
        "A booking has already been cancelled.",
        [
            "Open the cancelled booking.",
            "Attempt to cancel it again.",
        ],
        "No second seat is restored.",
    ),
    TestCase(
        "FB-008",
        "Data",
        "Booking survives application restart",
        "High",
        "A confirmed booking exists.",
        [
            "Close the application.",
            "Restart the application.",
            "Open the booking list.",
        ],
        "The booking and its status are still present.",
    ),
    TestCase(
        "FB-009",
        "Concurrency",
        "Two people request the last seat",
        "High",
        "A flight has exactly one seat left.",
        [
            "Start two booking requests at nearly the same time.",
            "Wait for both results.",
        ],
        "Exactly one booking succeeds; seats never drops below zero.",
    ),
    TestCase(
        "FB-010",
        "Accessibility",
        "Complete a booking using a keyboard",
        "High",
        "The booking interface is open.",
        [
            "Navigate using Tab and Shift+Tab.",
            "Enter passenger details.",
            "Confirm using the keyboard.",
        ],
        "Controls are reachable, focus is visible, and booking succeeds.",
    ),
    TestCase(
        "FB-011",
        "Accessibility",
        "Validation error is announced",
        "Medium",
        "A screen reader is active.",
        [
            "Submit the booking form with a blank name.",
            "Listen to the screen reader output.",
        ],
        "The error is announced and identifies the passenger-name field.",
    ),
    TestCase(
        "FB-012",
        "Security",
        "Booking reference does not grant access to another user",
        "High",
        "Two separate user accounts have bookings.",
        [
            "Sign in as user A.",
            "Request user B's booking reference.",
        ],
        "Access is denied and user B's details are not shown.",
    ),
]


for case in test_cases:
    print(f"\n{case.id} | {case.feature} | {case.priority}")
    print("Title:", case.title)
    print("Precondition:", case.precondition)

    for number, step in enumerate(case.steps, start=1):
        print(f"{number}. {step}")

    print("Expected:", case.expected_result)

print(f"\nTotal test cases: {len(test_cases)}")
print("Features covered:", sorted({case.feature for case in test_cases}))