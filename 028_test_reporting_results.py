# test_reporting.py
# Run with: python test_reporting.py

from collections import Counter
from dataclasses import dataclass
from datetime import date


@dataclass
class TestCase:
    id: str
    name: str
    requirement: str
    result: str  # Pass, Fail, Blocked, or Not Run
    defect_id: str = ""


@dataclass
class TestPlan:
    title: str
    objective: str
    scope: list[str]
    out_of_scope: list[str]
    environment: str
    approach: str
    entry_criteria: list[str]
    exit_criteria: list[str]
    risks: list[str]
    owner: str


plan = TestPlan(
    title="Task Tracker — Release 1 Test Plan",
    objective="Verify core task features before release.",
    scope=["Create tasks", "Complete tasks", "Basic accessibility"],
    out_of_scope=["Mobile app", "Performance testing"],
    environment="Chrome on Windows; staging database",
    approach="Manual scenarios plus automated regression checks",
    entry_criteria=[
        "Features deployed to staging",
        "Test accounts available",
        "Test data prepared",
    ],
    exit_criteria=[
        "All planned tests executed",
        "At least 90% of tests pass",
        "No open high-severity defects",
    ],
    risks=["Staging environment may become unavailable"],
    owner="QA team",
)

tests = [
    TestCase("TC-01", "Create a valid task", "REQ-01", "Pass"),
    TestCase("TC-02", "Reject a blank title", "REQ-01", "Pass"),
    TestCase("TC-03", "Complete a task", "REQ-02", "Fail", "BUG-17"),
    TestCase("TC-04", "Keyboard access to Add button", "REQ-03", "Pass"),
    TestCase("TC-05", "Input has an accessible label", "REQ-03", "Blocked"),
    TestCase("TC-06", "Task remains after refresh", "REQ-04", "Not Run"),
]

open_defects = [
    {"id": "BUG-17", "severity": "High", "summary": "Task cannot be completed"}
]


def print_section(title, items):
    print(f"\n{title}")
    for item in items:
        print(f"- {item}")


def report_progress(test_cases):
    counts = Counter(test.result for test in test_cases)
    total = len(test_cases)
    executed = counts["Pass"] + counts["Fail"] + counts["Blocked"]

    print("\nTEST PROGRESS")
    print(f"Planned:  {total}")
    print(f"Executed: {executed}/{total} ({executed / total:.0%})")
    print(f"Passed:   {counts['Pass']}")
    print(f"Failed:   {counts['Fail']}")
    print(f"Blocked:  {counts['Blocked']}")
    print(f"Not run:  {counts['Not Run']}")

    return counts, total


def assess_completion(counts, total, defects):
    all_executed = counts["Not Run"] == 0
    pass_rate = counts["Pass"] / total if total else 0
    no_high_defects = not any(
        defect["severity"] == "High" for defect in defects
    )

    checks = {
        "All planned tests executed": all_executed,
        "At least 90% of tests pass": pass_rate >= 0.90,
        "No open high-severity defects": no_high_defects,
    }

    print("\nCOMPLETION CHECK")
    for criterion, met in checks.items():
        print(f"{'MET' if met else 'NOT MET'}: {criterion}")

    print(
        "Release recommendation:",
        "READY" if all(checks.values()) else "NOT READY",
    )


print("=" * 50)
print(plan.title)
print("Report date:", date.today().isoformat())
print("Owner:", plan.owner)
print("Objective:", plan.objective)
print("Environment:", plan.environment)
print("Approach:", plan.approach)

print_section("IN SCOPE", plan.scope)
print_section("OUT OF SCOPE", plan.out_of_scope)
print_section("ENTRY CRITERIA", plan.entry_criteria)
print_section("EXIT CRITERIA", plan.exit_criteria)
print_section("RISKS", plan.risks)

counts, total = report_progress(tests)

print("\nTEST RESULTS")
for test in tests:
    defect = f" ({test.defect_id})" if test.defect_id else ""
    print(f"{test.id}: {test.name} — {test.result}{defect}")

print("\nOPEN DEFECTS")
for defect in open_defects:
    print(f"{defect['id']} [{defect['severity']}]: {defect['summary']}")

assess_completion(counts, total, open_defects)