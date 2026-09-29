# black_box_testing.py
# Run with: python black_box_testing.py

from itertools import product


def book_ticket(age, seats, coupon):
    """System under test: returns an observable result."""
    if not 18 <= age <= 120:
        return {"status": "REJECTED", "reason": "Invalid age"}
    if seats < 1:
        return {"status": "REJECTED", "reason": "No seats"}
    return {
        "status": "BOOKED",
        "price": 80 if coupon else 100,
    }


class Booking:
    def __init__(self):
        self.state = "NEW"

    def reserve(self):
        if self.state != "NEW":
            raise ValueError("Reservation not allowed")
        self.state = "BOOKED"

    def cancel(self):
        if self.state != "BOOKED":
            raise ValueError("Cancellation not allowed")
        self.state = "CANCELLED"


def check(label, actual, expected):
    assert actual == expected, f"{label}: {actual!r} != {expected!r}"
    print(f"PASS: {label}")


# 1. Equivalence partitioning:
# Choose a representative from each group of inputs.
equivalence_cases = [
    ("Age below valid range", 16, 2, False, "REJECTED"),
    ("Age in valid range", 35, 2, False, "BOOKED"),
    ("Age above valid range", 125, 2, False, "REJECTED"),
    ("No seats", 35, 0, False, "REJECTED"),
]

for label, age, seats, coupon, expected in equivalence_cases:
    check(label, book_ticket(age, seats, coupon)["status"], expected)


# 2. Boundary value analysis:
# Test just below, at, and just above each age boundary.
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
# Conditions: valid age, available seat, coupon.
# Actions: reject, book at full price, or book at discount.
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
    if price is not None:
        check(f"Decision rule {number} price", result["price"], price)


# 4. State-transition testing:
booking = Booking()
check("Initial state", booking.state, "NEW")
booking.reserve()
check("NEW -> BOOKED", booking.state, "BOOKED")
booking.cancel()
check("BOOKED -> CANCELLED", booking.state, "CANCELLED")

try:
    booking.reserve()
except ValueError:
    print("PASS: CANCELLED -> BOOKED is rejected")
else:
    raise AssertionError("Invalid state transition was accepted")


# 5. Pairwise testing:
# Generate a small set of cases in which every pair of factor values occurs.
factors = {
    "device": ["phone", "tablet", "desktop"],
    "network": ["wifi", "cellular", "offline"],
    "coupon": [False, True],
}

names = list(factors)
candidates = list(product(*(factors[name] for name in names)))

all_pairs = {
    (i, row[i], j, row[j])
    for row in candidates
    for i in range(len(names))
    for j in range(i + 1, len(names))
}

selected = []
uncovered = set(all_pairs)

while uncovered:
    best = max(
        candidates,
        key=lambda row: sum(
            (i, row[i], j, row[j]) in uncovered
            for i in range(len(names))
            for j in range(i + 1, len(names))
        ),
    )
    selected.append(best)

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            uncovered.discard((i, best[i], j, best[j]))

    candidates.remove(best)

print("\nPAIRWISE TEST CASES")
for number, row in enumerate(selected, start=1):
    print(number, dict(zip(names, row)))

check("All factor pairs covered", len(uncovered), 0)