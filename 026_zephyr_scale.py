# zephyr_scale_workflow_model.py
# Run with: python zephyr_scale_workflow_model.py
#
# A local practice model of Zephyr Scale concepts.
# This does not connect to a Zephyr Scale account or change Jira data.

import csv
from collections import Counter
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TestCase:
    key: str
    name: str
    folder: str
    objective: str
    precondition: str
    steps: list[tuple[str, str]]
    requirement: str
    parameters: dict[str, str] = field(default_factory=dict)
    calls: list[str] = field(default_factory=list)
    bdd: str = ""
    archived: bool = False


@dataclass
class TestCycle:
    name: str
    configuration: str
    case_keys: list[str]
    results: dict[str, str] = field(default_factory=dict)


@dataclass
class TestPlan:
    name: str
    cycle_names: list[str]


class TestLibrary:
    def __init__(self):
        self.cases: dict[str, TestCase] = {}
        self.cycles: dict[str, TestCycle] = {}
        self.plans: dict[str, TestPlan] = {}
        self.next_number = 1
        self.permissions = {
            "viewer": {"read"},
            "tester": {"read", "execute"},
            "manager": {"read", "execute", "create", "edit", "delete"},
        }

    def require(self, role: str, action: str) -> None:
        if action not in self.permissions.get(role, set()):
            raise PermissionError(f"{role} cannot {action}")

    def create_case(self, role: str, **details) -> TestCase:
        self.require(role, "create")
        key = f"DEMO-T{self.next_number}"
        self.next_number += 1
        case = TestCase(key=key, **details)
        self.cases[key] = case
        return case

    def bulk_create(self, role: str, definitions: list[dict]) -> list[TestCase]:
        return [self.create_case(role, **item) for item in definitions]

    def clone_case(self, role: str, key: str) -> TestCase:
        self.require(role, "create")
        original = deepcopy(self.cases[key])
        original.key = f"DEMO-T{self.next_number}"
        original.name += " (copy)"
        self.next_number += 1
        self.cases[original.key] = original
        return original

    def archive_case(self, role: str, key: str) -> None:
        self.require(role, "edit")
        self.cases[key].archived = True

    def delete_case(self, role: str, key: str) -> None:
        self.require(role, "delete")
        del self.cases[key]

    def create_cycle(
        self, role: str, name: str, configuration: str, keys: list[str]
    ) -> TestCycle:
        self.require(role, "create")
        if any(key not in self.cases for key in keys):
            raise ValueError("Cycle contains an unknown test case")
        cycle = TestCycle(name, configuration, keys)
        self.cycles[name] = cycle
        return cycle

    def execute(
        self, role: str, cycle_name: str, key: str, status: str
    ) -> None:
        self.require(role, "execute")
        if status not in {"Pass", "Fail", "Blocked"}:
            raise ValueError("Invalid execution status")
        cycle = self.cycles[cycle_name]
        if key not in cycle.case_keys:
            raise ValueError("Case is not in this cycle")
        cycle.results[key] = status

    def create_plan(
        self, role: str, name: str, cycle_names: list[str]
    ) -> TestPlan:
        self.require(role, "create")
        if any(name not in self.cycles for name in cycle_names):
            raise ValueError("Plan contains an unknown cycle")
        plan = TestPlan(name, cycle_names)
        self.plans[name] = plan
        return plan

    def export_cases(self, path: Path) -> None:
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
        with path.open(newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))

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
        links: dict[str, list[str]] = {}
        for case in self.cases.values():
            links.setdefault(case.requirement, []).append(case.key)
        return links

    def cycle_report(self, name: str) -> dict[str, int]:
        cycle = self.cycles[name]
        counts = Counter(cycle.results.values())
        counts["Not Run"] = len(cycle.case_keys) - len(cycle.results)
        return dict(counts)


library = TestLibrary()

# Folder, detailed test case, parameters, BDD, and requirement link.
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

# Call to test: the second case reuses the login steps.
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

# Data-driven variations use the same case with different parameters.
data_sets = [
    {"title": "Write README", "expected": "Pass"},
    {"title": "Test the app", "expected": "Pass"},
    {"title": "   ", "expected": "Fail"},
]

# Bulk creation, clone, archive, and delete.
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

temporary_copy = library.clone_case("manager", login.key)
library.archive_case("manager", temporary_copy.key)
library.delete_case("manager", temporary_copy.key)

# Test configuration, cycle execution, and plan.
cycle = library.create_cycle(
    "manager",
    name="Sprint 1 regression",
    configuration="Chrome / Windows / staging",
    keys=[login.key, create_task.key, *(case.key for case in new_cases)],
)

library.execute("tester", cycle.name, login.key, "Pass")
library.execute("tester", cycle.name, create_task.key, "Pass")
library.execute("tester", cycle.name, new_cases[0].key, "Fail")

plan = library.create_plan(
    "manager", "Release 1 test plan", [cycle.name]
)

# Export and import practice data.
export_path = Path("zephyr_practice_export.csv")
library.export_cases(export_path)

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

imported = library.import_case_names(
    "manager", import_path, "Tasks/Search"
)

print("Test cases:", list(library.cases))
print("Imported:", [case.key for case in imported])
print("Call to test:", create_task.calls)
print("Data sets:", data_sets)
print("Bidirectional traceability:")
for requirement, case_keys in library.traceability().items():
    print(f"  {requirement} -> {case_keys}")
for case in library.cases.values():
    print(f"  {case.key} -> {case.requirement}")
print("Cycle progress:", library.cycle_report(cycle.name))
print("Test plan:", plan.name, plan.cycle_names)
print("Export:", export_path)
``` :content-reference{index="0"}