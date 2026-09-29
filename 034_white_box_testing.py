# white_box_coverage.py
# Run with: python white_box_coverage.py

from dataclasses import dataclass, field


@dataclass
class Coverage:
    statements: set[str] = field(default_factory=set)
    decisions: set[bool] = field(default_factory=set)
    conditions: dict[str, set[bool]] = field(
        default_factory=lambda: {"A": set(), "B": set()}
    )
    paths: set[tuple[bool, str]] = field(default_factory=set)
    loop_counts: set[str] = field(default_factory=set)


coverage = Coverage()


def classify_loop(count: int) -> str:
    if count == 0:
        return "zero"
    if count == 1:
        return "one"
    return "multiple"


def calculate_discount(is_member: bool, has_coupon: bool, items: list[int]):
    coverage.statements.add("S1: initialize total")
    total = 0

    # Loop coverage: zero, one, and multiple iterations.
    loop_type = classify_loop(len(items))
    coverage.loop_counts.add(loop_type)

    for price in items:
        coverage.statements.add("S2: add item price")
        total += price

    # A and B are independently testable conditions.
    # Python short-circuits: B is evaluated only when A is True.
    coverage.conditions["A"].add(is_member)
    if is_member:
        coverage.conditions["B"].add(has_coupon)

    decision = is_member and has_coupon
    coverage.decisions.add(decision)
    coverage.paths.add((decision, loop_type))

    if decision:
        coverage.statements.add("S3: apply discount")
        total *= 0.9
    else:
        coverage.statements.add("S4: keep original total")

    coverage.statements.add("S5: return total")
    return round(total, 2)


# Each row is a test: (member, coupon, item prices, expected result).
tests = [
    (True,  True,  [],           0.00),   # True branch; zero loops
    (False, True,  [],           0.00),   # A independently changes outcome
    (True,  False, [100],      100.00),   # B independently changes outcome
    (True,  True,  [100],       90.00),   # True branch; one loop
    (False, True,  [40, 60],   100.00),   # False branch; multiple loops
    (True,  True,  [40, 60],    90.00),   # True branch; multiple loops
    (False, False, [100],      100.00),   # False branch; one loop
    (True,  False, [],           0.00),   # False branch; zero loops
]

for number, (member, coupon, items, expected) in enumerate(tests, start=1):
    actual = calculate_discount(member, coupon, items)
    assert actual == expected, f"Test {number}: {actual} != {expected}"
    print(f"Test {number}: PASS")


all_statements = {
    "S1: initialize total",
    "S2: add item price",
    "S3: apply discount",
    "S4: keep original total",
    "S5: return total",
}
all_paths = {
    (decision, loop_type)
    for decision in (False, True)
    for loop_type in ("zero", "one", "multiple")
}

# MC/DC pairs: change one condition while keeping the other fixed.
mcdc_a = (
    (True, True) in [(row[0], row[1]) for row in tests]
    and (False, True) in [(row[0], row[1]) for row in tests]
)
mcdc_b = (
    (True, True) in [(row[0], row[1]) for row in tests]
    and (True, False) in [(row[0], row[1]) for row in tests]
)

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

assert coverage.statements == all_statements
assert coverage.decisions == {False, True}
assert coverage.conditions["A"] == {False, True}
assert coverage.conditions["B"] == {False, True}
assert coverage.paths == all_paths
assert coverage.loop_counts == {"zero", "one", "multiple"}
assert mcdc_a and mcdc_b