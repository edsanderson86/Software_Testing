# zephyr_scale_workflow_model.py
# Run with: python zephyr_scale_workflow_model.py
#
# Model test-management concepts locally using Python objects.
# This script does not connect to an account or change Jira data.
# Cases, cycles, and plans remain in memory; selected case details are
# exported to CSV files in the current working directory.

import csv
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path


# Store a test's purpose, setup, action-and-result steps, and requirement link.
# Dataclasses generate initialization and other standard methods.
@dataclass
class TestCase:
    key: str
    name: str
    folder: str
    objective: str
    precondition: str
    steps: list[tuple[str, str]]
    requirement: str

    # Factories give each case its own dictionary and list.
    parameters: dict[str, str] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)
    bdd: str = ""
    archived: bool = False


# Group cases for a particular configuration and store their latest results.
@dataclass
class TestCycle:
    name: str
    configuration: str
    case_keys: list[str]
    results: dict[str, str] = field(default_factory=dict)


# Group named cycles under a broader testing plan.
@dataclass
class TestPlan:
    name: str
    cycle_names: list[str]


class TestLibrary:
    def __init__(self):
        # Keep independently addressable collections of cases, cycles, and plans.
        self.cases: dict[str, TestCase] = {}
        self.cycles: dict[str, TestCycle] = {}
        self.plans: dict[str, TestPlan] = {}
        self.next_number = 1

        # Define permissions for this practice model.
        # These roles are supplied by callers rather than authenticated.
        self.permissions = {
            "viewer": {"read"},
            "tester": {"read", "execute"},
            "manager": {"read", "execute", "create", "edit", "delete"},
        }

    def require(self, role: str, action: str) -> None:
        # Reject actions missing from the role's permission set.
        # Unknown roles receive no permissions.
        if action not in self.permissions.get(role, set()):
            raise PermissionError(f"{role} cannot {action}")

    def create_case(self, role: str, **details) -> TestCase:
        self.require(role, "create")

        # Generate a local identifier and store the supplied case details.
        key = f"DEMO-T{self.next_number}"
        self.next_number += 1
        case = TestCase(key=key, **details)
        self.cases[key] = case
        return case

    def bulk_create(self, role: str, definitions: list[dict]) -> list[TestCase]:
        # Create each case through the same permission-checked method.
        # This is sequential; earlier creations remain if a later one fails.
        return [self.create_case(role, **item) for item in definitions]

    def clone_case(self, role: str, key: str) -> TestCase:
        self.require(role, "create")

        # Copy nested values so editing the clone does not alter the original.
        original = deepcopy(self.cases[key])
        original.key = f"DEMO-T{self.next_number}"
        original.name += " (copy)"
        self.next_number += 1
        self.cases[original.key] = original
        return original

    def archive_case(self, role: str, key: str) -> None:
        # Mark the case as archived while retaining its stored details.
        # Other methods do not automatically exclude archived cases.
        self.require(role, "edit")
        self.cases[key].archived = True

    def delete_case(self, role: str, key: str) -> None:
        # Remove the case from the library.
        # This model does not remove references from existing cycles or calls.
        self.require(role, "delete")
        del self.cases[key]

    def create_cycle(
        self, role: str, name: str, configuration: str, keys: list[str]
    ) -> TestCycle:
        self.require(role, "create")

        # Ensure every selected case exists before storing the cycle.
        if any(key not in self.cases for key in keys):
            raise ValueError("Cycle contains an unknown test case")

        cycle = TestCycle(name, configuration, keys)
        self.cycles[name] = cycle
        return cycle

    def execute(
        self, role: str, cycle_name: str, key: str, status: str
    ) -> None:
        self.require(role, "execute")

        # Record a supplied outcome; this method does not run test steps.
        if status not in {"Pass", "Fail", "Blocked"}:
            raise ValueError("Invalid execution status")

        cycle = self.cycles[cycle_name]
        if key not in cycle.case_keys:
            raise ValueError("Case is not in this cycle")

        # A new result replaces any previous result for this case in the cycle.
        cycle.results[key] = status

    def create_plan(
        self, role: str, name: str, cycle_names: list[str]
    ) -> TestPlan:
        self.require(role, "create")

        # Prevent a plan from referring to cycles that do not exist.
        if any(name not in self.cycles for name in cycle_names):
            raise ValueError("Plan contains an unknown cycle")

        plan = TestPlan(name, cycle_names)
        self.plans[name] = plan
        return plan

    def export_cases(self, path: Path) -> None:
        # Export selected metadata, including archived cases.
        # Steps, parameters, calls, and BDD text are omitted.
        # This method has no role check and replaces an existing output file.
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "key", "name", "folder", "objective",
                    "precondition", "requirement", "archived",
                ],
            )
            writer.writeheader()
            for case in self.cases.values():
                writer.writerow({
                    field_name: getattr(case, field_name)
                    for field_name in writer.fieldnames
                })

    def import_case_names(
        self, role: str, path: Path, folder: str
    ) -> list[TestCase]:
        self.require(role, "create")

        # Read case metadata from a CSV with the expected column headings.
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

        # Create new cases with fresh IDs in the supplied folder.
        # This is a metadata import, not a complete restoration of exported cases.
        return self.bulk_create(role, [
            {
                "name": row["name"],
                "folder": folder,
                "objective": row["objective"],
                "precondition": row.get("precondition", ""),
                "steps": [],
                "requirement": row["requirement"],
            }
            for row in rows
        ])

    def traceability(self) -> dict[str, list[str]]:
        # Build a requirement-to-case lookup from the stored links.
        links: dict[str, list[str]] = {}
        for case in self.cases.values():
            links.setdefault(case.requirement, []).append(case.key)
        return links

    def cycle_report(self, name: str) -> dict[str, int]:
        # Count recorded outcomes and calculate how many cases remain unrun.
        # This calculation assumes each case key appears once in the cycle.
        cycle = self.cycles[name]
        counts = Counter(cycle.results.values())
        counts["Not Run"] = len(cycle.case_keys) - len(cycle.results)
        return dict(counts)


# Create an independent library for the demonstration.
library = TestLibrary()

# Define a login case with steps, example parameters, and a requirement link.
# Folder paths are labels in this model rather than filesystem directories.
# BDD text is stored for reference; it is not parsed or executed.
login = library.create_case(
    "manager",
    name="Valid login",
    folder="Authentication/Login",
    objective="A registered user can sign in",
    precondition="The user account exists",
    steps=[
        ("Enter {username} and {password}", "Credentials are accepted"),
        ("Select Sign in", "The dashboard appears"),
    ],
    requirement="APP-101",
    parameters={"username": "alex", "password": "valid-test-password"},
    bdd="""Feature: Login
  Scenario Outline: Valid credentials
    Given a registered user "<username>"
    When they sign in with "<password>"
    Then the dashboard is displayed

    Examples:
      | username | password            |
      | alex     | valid-test-password |
      | sam      | another-test-value  |
""",
)

# Store a reference to the login case as a reusable setup relationship.
# The calls list records the relationship without executing the referenced case.
create_task = library.create_case(
    "manager",
    name="Create a task",
    folder="Tasks/Create",
    objective="A signed-in user can create a task",
    precondition="A user account exists",
    steps=[
        ("Enter {title}", "The title appears in the form"),
        ("Select Add task", "The task appears in the list"),
    ],
    requirement="APP-202",
    parameters={"title": "Write README"},
    calls=[login.key],
)

# Define sample input variations for reference; no loop executes them here.
# The blank-title entry labels task creation as unsuccessful.
# A validation test would pass when the application correctly rejects it.
data_sets = [
    {"title": "Write README", "expected": "Pass"},
    {"title": "Test the app", "expected": "Pass"},
    {"title": "   ", "expected": "Fail"},
]

# Create multiple cases from a list of definitions.
new_cases = library.bulk_create("manager", [
    {
        "name": "Complete a task",
        "folder": "Tasks/Complete",
        "objective": "Mark an open task complete",
        "precondition": "An open task exists",
        "steps": [("Select Complete", "Status changes to complete")],
        "requirement": "APP-203",
    },
    {
        "name": "Reject blank title",
        "folder": "Tasks/Create",
        "objective": "Prevent empty task names",
        "precondition": "The task form is open",
        "steps": [("Submit spaces", "An error is displayed")],
        "requirement": "APP-202",
    },
])

# Demonstrate copying, archiving, and deleting a temporary case.
# The original login case remains in the library.
temporary_copy = library.clone_case("manager", login.key)
library.archive_case("manager", temporary_copy.key)
library.delete_case("manager", temporary_copy.key)

# Group four cases into a cycle with a descriptive environment label.
# The configuration does not launch a browser or configure an environment.
cycle = library.create_cycle(
    "manager",
    name="Sprint 1 regression",
    configuration="Chrome / Windows / staging",
    keys=[login.key, create_task.key, *(case.key for case in new_cases)],
)

# Record sample results, leaving the blank-title case as Not Run.
library.execute("tester", cycle.name, login.key, "Pass")
library.execute("tester", cycle.name, create_task.key, "Pass")
library.execute("tester", cycle.name, new_cases[0].key, "Fail")

# Associate the cycle with a release-level plan.
plan = library.create_plan(
    "manager", "Release 1 test plan", [cycle.name]
)

# Export current case metadata before adding the imported search case.
export_path = Path("zephyr_practice_export.csv")
library.export_cases(export_path)

# Create a separate CSV to demonstrate the expected import format.
import_path = Path("zephyr_practice_import.csv")
with import_path.open("w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["name", "objective", "precondition", "requirement"],
    )
    writer.writeheader()
    writer.writerow({
        "name": "Search tasks",
        "objective": "Find a task by title",
        "precondition": "Tasks exist",
        "requirement": "APP-204",
    })

# Import the search case into the library.
# It is not automatically added to the existing cycle or earlier export.
imported = library.import_case_names(
    "manager", import_path, "Tasks/Search"
)

# Display stored cases, reuse references, and example input variations.
print("Test cases:", list(library.cases))
print("Imported:", [case.key for case in imported])
print("Call to test:", create_task.calls)
print("Data sets:", data_sets)

# Show requirement links in both directions using the same stored data.
print("Bidirectional traceability:")
for requirement, case_keys in library.traceability().items():
    print(f"  {requirement} -> {case_keys}")
for case in library.cases.values():
    print(f"  {case.key} -> {case.requirement}")

# Summarize the recorded cycle results and plan membership.
print("Cycle progress:", library.cycle_report(cycle.name))
print("Test plan:", plan.name, plan.cycle_names)
print("Export:", export_path)