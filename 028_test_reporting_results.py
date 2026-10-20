# test_reporting.py
# Run with: python test_reporting.py
# Present a test plan, summarize recorded outcomes, and assess release criteria.
# This script reports supplied sample data; it does not execute tests.

from collections import Counter
from dataclasses import dataclass
from datetime import date


# Store each test's identity, requirement link, outcome, and optional defect link.
@dataclass
class TestCase:
    id: str
    name: str
    requirement: str
    result: str  # Expected values: Pass, Fail, Blocked, or Not Run.
    defect_id: str = ""


# Group planning information so the report explains what testing covers,
# how it is approached, and which conditions govern completion.
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


# Define the release's test plan.
# Entry criteria are displayed for reference rather than evaluated by this code.
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

# Supply representative results, including a failed test linked to a defect.
# Requirement identifiers provide traceability back to the tested behaviour.
tests = [
    TestCase("TC-01", "Create a valid task", "REQ-01", "Pass"),
    TestCase("TC-02", "Reject a blank title", "REQ-01", "Pass"),
    TestCase("TC-03", "Complete a task", "REQ-02", "Fail", "BUG-17"),
    TestCase("TC-04", "Keyboard access to Add button", "REQ-03", "Pass"),
    TestCase("TC-05", "Input has an accessible label", "REQ-03", "Blocked"),
    TestCase("TC-06", "Task remains after refresh", "REQ-04", "Not Run"),
]

# Treat every defect in this list as currently open.
open_defects = [
    {"id": "BUG-17", "severity": "High", "summary": "Task cannot be completed"}
]


def print_section(title, items):
    # Use consistent formatting for the plan's list-based sections.
    print(f"\n{title}")
    for item in items:
        print(f"- {item}")


def report_progress(test_cases):
    # Count the recorded outcomes and calculate progress against the total.
    counts = Counter(test.result for test in test_cases)
    total = len(test_cases)

    # This report includes Blocked in its executed count.
    # A blocked outcome does not establish that all test steps were completed.
    executed = counts["Pass"] + counts["Fail"] + counts["Blocked"]

    # The percentage calculation assumes at least one planned test.
    print("\nTEST PROGRESS")
    print(f"Planned:  {total}")
    print(f"Executed: {executed}/{total} ({executed / total:.0%})")
    print(f"Passed:   {counts['Pass']}")
    print(f"Failed:   {counts['Fail']}")
    print(f"Blocked:  {counts['Blocked']}")
    print(f"Not run:  {counts['Not Run']}")

    return counts, total


def assess_completion(counts, total, defects):
    # Follow this example's convention that only Not Run prevents
    # the execution criterion from being met; Blocked does not prevent it.
    all_executed = counts["Not Run"] == 0

    # Calculate the pass rate against all planned tests.
    # Failed, blocked, and unrun cases therefore reduce this percentage.
    pass_rate = counts["Pass"] / total if total else 0

    # Look for open defects whose severity is exactly "High".
    no_high_defects = not any(
        defect["severity"] == "High" for defect in defects
    )

    # Evaluate rules that mirror the plan's exit criteria.
    # These rules are defined separately from the plan's descriptive text.
    checks = {
        "All planned tests executed": all_executed,
        "At least 90% of tests pass": pass_rate >= 0.90,
        "No open high-severity defects": no_high_defects,
    }

    print("\nCOMPLETION CHECK")
    for criterion, met in checks.items():
        print(f"{'MET' if met else 'NOT MET'}: {criterion}")

    # Recommend readiness only when every evaluated criterion is met.
    print(
        "Release recommendation:",
        "READY" if all(checks.values()) else "NOT READY",
    )


# Display the report context using the computer's current local date.
print("=" * 50)
print(plan.title)
print("Report date:", date.today().isoformat())
print("Owner:", plan.owner)
print("Objective:", plan.objective)
print("Environment:", plan.environment)
print("Approach:", plan.approach)

# Present scope, prerequisites, completion conditions, and known risks.
print_section("IN SCOPE", plan.scope)
print_section("OUT OF SCOPE", plan.out_of_scope)
print_section("ENTRY CRITERIA", plan.entry_criteria)
print_section("EXIT CRITERIA", plan.exit_criteria)
print_section("RISKS", plan.risks)

# Summarize recorded progress before showing individual results.
counts, total = report_progress(tests)

# Include defect references beside affected tests.
print("\nTEST RESULTS")
for test in tests:
    defect = f" ({test.defect_id})" if test.defect_id else ""
    print(f"{test.id}: {test.name} — {test.result}{defect}")

# Show unresolved defects that inform the completion assessment.
print("\nOPEN DEFECTS")
for defect in open_defects:
    print(f"{defect['id']} [{defect['severity']}]: {defect['summary']}")

# Assess the supplied results and defects against the release rules.
# With this sample data, the recommendation is NOT READY.
assess_completion(counts, total, open_defects)