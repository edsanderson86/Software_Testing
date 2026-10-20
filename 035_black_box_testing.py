# black_box_testing.py
# Run with: python black_box_testing.py
# Demonstrate test design based on inputs, outputs, and observable states.
# Examples cover equivalence partitions, boundaries, decision rules,
# state transitions, and generation of pairwise input combinations.

from itertools import product


def book_ticket(age, seats, coupon):
    # Provide a small system under test with observable booking outcomes.
    # These checks assume numeric age and seats values.
    if not 18 <= age <= 120:
        return {"status": "REJECTED", "reason": "Invalid age"}
    if seats < 1:
        return {"status": "REJECTED", "reason": "No seats"}

    # Return a sample price without reserving or decrementing any seats.
    return {
        "status": "BOOKED",
        "price": 80 if coupon else 100,
    }


class Booking:
    def __init__(self):
        # Begin each booking in the initial state.
        self.state = "NEW"

    def reserve(self):
        # Allow reservation only before a booking has been made.
        if self.state != "NEW":
            raise ValueError("Reservation not allowed")
        self.state = "BOOKED"

    def cancel(self):
        # Allow cancellation only for a currently booked reservation.
        if self.state != "BOOKED":
            raise ValueError("Cancellation not allowed")
        self.state = "CANCELLED"


def check(label, actual, expected):
    # Compare an observable result with its expected value.
    # A mismatch stops execution with a descriptive assertion error.
    assert actual == expected, f"{label}: {actual!r} != {expected!r}"
    print(f"PASS: {label}")


# 1. Equivalence partitioning:
# Select representative inputs from groups expected to behave similarly.
# Keep other inputs valid when isolating age or seat availability.
equivalence_cases = [
    ("Age below valid range", 16, 2, False, "REJECTED"),
    ("Age in valid range", 35, 2, False, "BOOKED"),
    ("Age above valid range", 125, 2, False, "REJECTED"),
    ("No seats", 35, 0, False, "REJECTED"),
]

for label, age, seats, coupon, expected in equivalence_cases:
    check(label, book_ticket(age, seats, coupon)["status"], expected)


# 2. Boundary value analysis:
# Exercise values immediately below, at, and above the inclusive age limits.
# Hold seat availability and coupon status constant.
boundary_cases = [
    (17, "REJECTED"),
    (18, "BOOKED"),
    (19, "BOOKED"),
    (119, "BOOKED"),
    (120, "BOOKED"),
    (121, "REJECTED"),
]

for age, expected in boundary_cases:
    check(
        f"Age boundary {age}",
        book_ticket(age, 1, False)["status"],
        expected,
    )


# 3. Decision table testing:
# Combine age validity, seat availability, and coupon status.
# These selected rules cover rejection and both booking prices.
# They omit combinations where age is invalid and seats are unavailable.
decision_table = [
    # age, seats, coupon, expected status, expected price
    (16, 1, False, "REJECTED", None),
    (16, 1, True,  "REJECTED", None),
    (30, 0, False, "REJECTED", None),
    (30, 0, True,  "REJECTED", None),
    (30, 1, False, "BOOKED",   100),
    (30, 1, True,  "BOOKED",    80),
]

for number, (age, seats, coupon, status, price) in enumerate(
    decision_table, start=1
):
    result = book_ticket(age, seats, coupon)
    check(f"Decision rule {number} status", result["status"], status)

    # Check prices only for rules that expect a successful booking.
    if price is not None:
        check(f"Decision rule {number} price", result["price"], price)


# 4. State-transition testing:
# Verify a valid sequence from creation through reservation to cancellation.
booking = Booking()
check("Initial state", booking.state, "NEW")

booking.reserve()
check("NEW -> BOOKED", booking.state, "BOOKED")

booking.cancel()
check("BOOKED -> CANCELLED", booking.state, "CANCELLED")

# Attempt an invalid transition from the cancelled state.
# Other invalid transitions are not exercised in this example.
try:
    booking.reserve()
except ValueError:
    print("PASS: CANCELLED -> BOOKED is rejected")
else:
    raise AssertionError("Invalid state transition was accepted")


# 5. Pairwise testing:
# Define factors for a separate input-combination exercise.
# These combinations are generated but not executed against book_ticket().
factors = {
    "device": ["phone", "tablet", "desktop"],
    "network": ["wifi", "cellular", "offline"],
    "coupon": [False, True],
}

# Build all possible combinations as candidates for selection.
names = list(factors)
candidates = list(product(*(factors[name] for name in names)))

# Identify every pair of values belonging to two different factors.
# Factor positions distinguish pairs even when values happen to match.
all_pairs = {
    (i, row[i], j, row[j])
    for row in candidates
    for i in range(len(names))
    for j in range(i + 1, len(names))
}

selected = []
uncovered = set(all_pairs)

while uncovered:
    # Greedily choose the candidate covering the most outstanding pairs.
    # This produces a covering set without guaranteeing the smallest set.
    best = max(
        candidates,
        key=lambda row: sum(
            (i, row[i], j, row[j]) in uncovered
            for i in range(len(names))
            for j in range(i + 1, len(names))
        ),
    )
    selected.append(best)

    # Remove the pairs covered by this selection from the outstanding set.
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            uncovered.discard((i, best[i], j, best[j]))

    # Prevent the same combination from being selected again.
    candidates.remove(best)

# Display the selected combinations with readable factor names.
print("\nPAIRWISE TEST CASES")
for number, row in enumerate(selected, start=1):
    print(number, dict(zip(names, row)))

# Verify pair coverage for the declared factor values.
# Pair coverage does not guarantee coverage of all three-factor interactions.
check("All factor pairs covered", len(uncovered), 0)