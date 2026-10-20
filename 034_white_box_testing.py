# white_box_coverage.py
# Run with: python white_box_coverage.py
# Demonstrate manually recorded statement, decision, condition, loop,
# and grouped path coverage, plus MC/DC input pairs.
# Coverage applies to the selected markers rather than every Python statement.

from dataclasses import dataclass, field


# Store unique observations so repeated execution does not inflate coverage.
@dataclass
class Coverage:
    statements: set[str] = field(default_factory=set)
    decisions: set[bool] = field(default_factory=set)

    # Track each condition's observed values when it is evaluated.
    conditions: dict[str, set[bool]] = field(
        default_factory=lambda: {"A": set(), "B": set()}
    )

    # Group paths by the discount decision and loop-iteration category.
    # These groups do not represent every possible execution path.
    paths: set[tuple[bool, str]] = field(default_factory=set)
    loop_counts: set[str] = field(default_factory=set)


# Accumulate observations across all test cases in this run.
coverage = Coverage()


def classify_loop(count: int) -> str:
    # Group list lengths into three loop-testing categories.
    if count == 0:
        return "zero"
    if count == 1:
        return "one"
    return "multiple"


def calculate_discount(is_member: bool, has_coupon: bool, items: list[int]):
    # Mark initialization as reached and start the running total.
    coverage.statements.add("S1: initialize total")
    total = 0

    # Record whether the summation loop will run zero, one, or multiple times.
    loop_type = classify_loop(len(items))
    coverage.loop_counts.add(loop_type)

    for price in items:
        # This marker is reached only when the list contains an item.
        coverage.statements.add("S2: add item price")
        total += price

    # Treat membership as condition A and coupon availability as condition B.
    # Mirror Python's short-circuit behaviour: B contributes an evaluated
    # outcome only when A is true.
    coverage.conditions["A"].add(is_member)
    if is_member:
        coverage.conditions["B"].add(has_coupon)

    # Record the combined decision and its grouped loop path.
    decision = is_member and has_coupon
    coverage.decisions.add(decision)
    coverage.paths.add((decision, loop_type))

    if decision:
        # Apply a 10% discount only when both conditions are true.
        coverage.statements.add("S3: apply discount")
        total *= 0.9
    else:
        # Record the alternative branch, which leaves the total unchanged.
        coverage.statements.add("S4: keep original total")

    coverage.statements.add("S5: return total")
    return round(total, 2)


# Each row supplies membership, coupon availability, prices, and expected total.
# The combinations cover both decision outcomes within each loop category.
tests = [
    (True,  True,  [],           0.00),   # Discount branch; zero iterations.
    (False, True,  [],           0.00),   # A changes the decision versus row 1.
    (True,  False, [100],      100.00),   # B changes the decision versus row 4.
    (True,  True,  [100],       90.00),   # Discount branch; one iteration.
    (False, True,  [40, 60],   100.00),   # No discount; multiple iterations.
    (True,  True,  [40, 60],    90.00),   # Discount; multiple iterations.
    (False, False, [100],      100.00),   # No discount; B is short-circuited.
    (True,  False, [],           0.00),   # No discount; zero iterations.
]

# Execute every case and verify its calculated result.
# Coverage alone would not establish that the returned totals are correct.
for number, (member, coupon, items, expected) in enumerate(tests, start=1):
    actual = calculate_discount(member, coupon, items)
    assert actual == expected, f"Test {number}: {actual} != {expected}"
    print(f"Test {number}: PASS")


# Define the five selected statement markers expected across the suite.
all_statements = {
    "S1: initialize total",
    "S2: add item price",
    "S3: apply discount",
    "S4: keep original total",
    "S5: return total",
}

# Define six grouped paths: two decisions multiplied by three loop categories.
# Different counts within "multiple" are deliberately treated as one category.
all_paths = {
    (decision, loop_type)
    for decision in (False, True)
    for loop_type in ("zero", "one", "multiple")
}

# Check for MC/DC input pairs for the expression A and B.
# With B held true, changing A changes the decision.
# These checks inspect supplied inputs rather than recorded decision traces.
mcdc_a = (
    (True, True) in [(row[0], row[1]) for row in tests]
    and (False, True) in [(row[0], row[1]) for row in tests]
)

# With A held true, changing B changes the decision.
# A changed decision need not change the total when the basket is empty.
mcdc_b = (
    (True, True) in [(row[0], row[1]) for row in tests]
    and (True, False) in [(row[0], row[1]) for row in tests]
)

# Display the observations collected during execution.
print("\nCOVERAGE REPORT")
print(
    "Statement coverage:",
    f"{len(coverage.statements & all_statements)}/{len(all_statements)}",
)
print("Decision coverage:", coverage.decisions, "expected {False, True}")
print("Condition A outcomes:", coverage.conditions["A"])
print("Condition B outcomes:", coverage.conditions["B"])
print("Path coverage:", f"{len(coverage.paths)}/{len(all_paths)}")
print("Loop coverage:", coverage.loop_counts)
print("MC/DC — A independently affects decision:", mcdc_a)
print("MC/DC — B independently affects decision:", mcdc_b)

# Fail the run if any selected coverage target or MC/DC input pair is missing.
# Run Python normally; optimized mode disables assert statements.
assert coverage.statements == all_statements
assert coverage.decisions == {False, True}
assert coverage.conditions["A"] == {False, True}
assert coverage.conditions["B"] == {False, True}
assert coverage.paths == all_paths
assert coverage.loop_counts == {"zero", "one", "multiple"}
assert mcdc_a and mcdc_b