# test_execution_and_defects.py
# Run with: python test_execution_and_defects.py

from dataclasses import dataclass, field
from enum import Enum


class DefectStatus(Enum):
    NEW = "New"
    TRIAGED = "Triaged"
    IN_PROGRESS = "In Progress"
    READY_FOR_RETEST = "Ready for Retest"
    CLOSED = "Closed"
    REOPENED = "Reopened"


@dataclass
class TestResult:
    name: str
    passed: bool
    actual: str


@dataclass
class Defect:
    id: int
    title: str
    steps: list[str]
    expected: str
    actual: str
    impact: str
    status: DefectStatus = DefectStatus.NEW
    severity: str = "Unassigned"
    priority: str = "Unassigned"
    history: list[str] = field(default_factory=list)

    def move_to(self, new_status: DefectStatus) -> None:
        allowed = {
            DefectStatus.NEW: {DefectStatus.TRIAGED},
            DefectStatus.TRIAGED: {DefectStatus.IN_PROGRESS},
            DefectStatus.IN_PROGRESS: {DefectStatus.READY_FOR_RETEST},
            DefectStatus.READY_FOR_RETEST: {
                DefectStatus.CLOSED,
                DefectStatus.REOPENED,
            },
            DefectStatus.REOPENED: {DefectStatus.IN_PROGRESS},
            DefectStatus.CLOSED: set(),
        }

        if new_status not in allowed[self.status]:
            raise ValueError(
                f"Invalid transition: {self.status.value} -> {new_status.value}"
            )

        self.history.append(f"{self.status.value} -> {new_status.value}")
        self.status = new_status


def run_accessibility_tests(page: dict) -> list[TestResult]:
    """Run simple checks against a model of a web page."""
    checks = [
        TestResult(
            name="Image has alternative text",
            passed=bool(page["image_alt"].strip()),
            actual=f"alt={page['image_alt']!r}",
        ),
        TestResult(
            name="Input has a visible label",
            passed=bool(page["input_label"].strip()),
            actual=f"label={page['input_label']!r}",
        ),
        TestResult(
            name="Button is reachable by keyboard",
            passed=page["button_keyboard_reachable"],
            actual=(
                "Reachable"
                if page["button_keyboard_reachable"]
                else "Not reachable with Tab"
            ),
        ),
    ]
    return checks


def report_defects(results: list[TestResult]) -> list[Defect]:
    expected_results = {
        "Image has alternative text": "Image conveys its purpose in text.",
        "Input has a visible label": "The input has an associated label.",
        "Button is reachable by keyboard": (
            "The button can be reached and activated without a mouse."
        ),
    }

    impacts = {
        "Image has alternative text": (
            "A screen reader user may miss the image's meaning."
        ),
        "Input has a visible label": (
            "A user may not know what information to enter."
        ),
        "Button is reachable by keyboard": (
            "A keyboard-only user cannot operate the button."
        ),
    }

    defects = []
    for result in results:
        if result.passed:
            continue

        defects.append(
            Defect(
                id=len(defects) + 1,
                title=result.name,
                steps=[
                    "Open the task creation page.",
                    f"Check: {result.name}.",
                ],
                expected=expected_results[result.name],
                actual=result.actual,
                impact=impacts[result.name],
            )
        )

    return defects


def triage(defect: Defect) -> None:
    """Example triage decision based on user impact."""
    if "cannot operate" in defect.impact:
        defect.severity = "High"
        defect.priority = "P1"
    else:
        defect.severity = "Medium"
        defect.priority = "P2"

    defect.move_to(DefectStatus.TRIAGED)


def print_report(defect: Defect) -> None:
    print(f"\nDEFECT {defect.id}: {defect.title}")
    print("Status:", defect.status.value)
    print("Severity:", defect.severity)
    print("Priority:", defect.priority)
    print("Steps:", " -> ".join(defect.steps))
    print("Expected:", defect.expected)
    print("Actual:", defect.actual)
    print("Impact:", defect.impact)
    print("Lifecycle:", " | ".join(defect.history))


# Test execution: deliberately faulty page.
page = {
    "image_alt": "",
    "input_label": "Task title",
    "button_keyboard_reachable": False,
}

results = run_accessibility_tests(page)

print("TEST EXECUTION")
for result in results:
    status = "PASS" if result.passed else "FAIL"
    print(f"{status}: {result.name} — {result.actual}")

defects = report_defects(results)

print("\nDEFECT TRIAGE")
for defect in defects:
    triage(defect)
    print(f"Defect {defect.id}: {defect.severity}, {defect.priority}")

# Simulate development and retesting of the keyboard defect.
keyboard_defect = next(
    defect for defect in defects
    if defect.title == "Button is reachable by keyboard"
)

keyboard_defect.move_to(DefectStatus.IN_PROGRESS)
page["button_keyboard_reachable"] = True
keyboard_defect.move_to(DefectStatus.READY_FOR_RETEST)

retest = next(
    result for result in run_accessibility_tests(page)
    if result.name == keyboard_defect.title
)

if retest.passed:
    keyboard_defect.move_to(DefectStatus.CLOSED)
else:
    keyboard_defect.move_to(DefectStatus.REOPENED)

print("\nDEFECT REPORTS")
for defect in defects:
    print_report(defect)

print("\nRetest result:", "PASS" if retest.passed else "FAIL")