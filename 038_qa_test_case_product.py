# flight_booking_test_design.py
# Run with: python flight_booking_test_design.py
# Present a test design covering flight search, booking, cancellation,
# persistence, concurrency, accessibility, and access control.
# This script prints test specifications; it does not execute the tests.

from dataclasses import dataclass


# Use a consistent structure so each case explains its purpose,
# importance, required setup, actions, and expected outcome.
@dataclass
class TestCase:
    id: str
    feature: str
    title: str
    priority: str
    precondition: str
    steps: list[str]
    expected_result: str


# Assign stable identifiers so cases can be referenced in results and defects.
# Priorities guide execution order but do not enforce it in this script.
test_cases = [
    # Verify the main search journey using a known route with available seats.
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

    # Check that an empty result is explained clearly to the user.
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

    # Exercise the availability boundary between one remaining seat and none.
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

    # Verify rejection at zero availability without changing stored data.
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

    # Ensure invalid passenger details do not consume a seat.
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

    # Verify that cancellation updates both booking status and availability.
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

    # Check that a repeated sequential cancellation cannot inflate availability.
    # Simultaneous cancellation requests would require a separate case.
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

    # Verify persistence by restarting and retrieving an existing booking.
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

    # Exercise competing requests for a single remaining seat.
    # Execution should coordinate requests to overlap and inspect stored results.
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

    # Assess keyboard operation and focus visibility in a graphical interface.
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

    # Check that validation feedback is available through a screen reader.
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

    # Verify booking ownership checks using two controlled test accounts.
    # Knowing a reference alone must not expose another account's booking.
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


# Print each specification with its setup and numbered actions.
# No result is assigned because the actions have not been executed.
for case in test_cases:
    print(f"\n{case.id} | {case.feature} | {case.priority}")
    print("Title:", case.title)
    print("Precondition:", case.precondition)

    for number, step in enumerate(case.steps, start=1):
        print(f"{number}. {step}")

    print("Expected:", case.expected_result)

# Summarize the number of designed cases and their distinct feature labels.
# Listed features indicate planned coverage rather than verified behaviour.
print(f"\nTotal test cases: {len(test_cases)}")
print("Features covered:", sorted({case.feature for case in test_cases}))