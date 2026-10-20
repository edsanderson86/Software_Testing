# test_execution_and_defects.py
# Run with: python test_execution_and_defects.py
# Demonstrate test execution, defect reporting, triage, and retesting.
# Checks use a simplified page model rather than inspecting a real browser.
# They illustrate selected accessibility concerns, not a complete assessment.

from dataclasses import dataclass, field
from enum import Enum


# Define named states for the example defect workflow.
class DefectStatus(Enum):
    NEW = "New"
    TRIAGED = "Triaged"
    IN_PROGRESS = "In Progress"
    READY_FOR_RETEST = "Ready for Retest"
    CLOSED = "Closed"
    REOPENED = "Reopened"


# Store a check's name, outcome, and observed result.
@dataclass
class TestResult:
    name: str
    passed: bool
    actual: str


# Keep the evidence, impact, classification, and lifecycle of a defect together.
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

    # Give each defect its own independent transition history.
    history: list[str] = field(default_factory=list)

    def move_to(self, new_status: DefectStatus) -> None:
        # Specify the permitted next states for each lifecycle stage.
        # This example treats Closed as a final state.
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

        # Reject an invalid transition before changing the defect.
        if new_status not in allowed[self.status]:
            raise ValueError(
                f"Invalid transition: {self.status.value} -> {new_status.value}"
            )

        # Record the transition and update the current status.
        self.history.append(f"{self.status.value} -> {new_status.value}")
        self.status = new_status


def run_accessibility_tests(page: dict) -> list[TestResult]:
    # Evaluate values supplied by the page model.
    # Non-empty text alone does not establish that alternative text is useful
    # or that a visible label is correctly associated with an input.
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
            # Read the model's flag; keyboard activation is not tested here.
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
    # Map each known check to its expected behaviour.
    expected_results = {
        "Image has alternative text": "Image conveys its purpose in text.",
        "Input has a visible label": "The input has an associated label.",
        "Button is reachable by keyboard": (
            "The button can be reached and activated without a mouse."
        ),
    }

    # Describe the potential user impact associated with each failure.
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
        # Passing checks do not generate defects.
        if result.passed:
            continue

        # Create a report using the observed result and predefined context.
        # IDs are sequential within this report batch, not globally unique.
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
    # Apply a simple example rule for severity and repair priority.
    # The rule depends on wording in the impact text and is illustrative.
    if "cannot operate" in defect.impact:
        defect.severity = "High"
        defect.priority = "P1"
    else:
        defect.severity = "Medium"
        defect.priority = "P2"

    # Move the newly reported defect into the triaged state.
    defect.move_to(DefectStatus.TRIAGED)


def print_report(defect: Defect) -> None:
    # Display the original evidence alongside the current lifecycle status.
    print(f"\nDEFECT {defect.id}: {defect.title}")
    print("Status:", defect.status.value)
    print("Severity:", defect.severity)
    print("Priority:", defect.priority)
    print("Steps:", " -> ".join(defect.steps))
    print("Expected:", defect.expected)
    print("Actual:", defect.actual)
    print("Impact:", defect.impact)
    print("Lifecycle:", " | ".join(defect.history))


# Start with missing alternative text and an unreachable button.
# The input label is populated, so that model check should pass.
page = {
    "image_alt": "",
    "input_label": "Task title",
    "button_keyboard_reachable": False,
}

# Execute the checks and display their initial outcomes.
results = run_accessibility_tests(page)

print("TEST EXECUTION")
for result in results:
    status = "PASS" if result.passed else "FAIL"
    print(f"{status}: {result.name} — {result.actual}")

# Convert the two failed checks into new defect records.
defects = report_defects(results)

# Classify each defect and advance it to the triaged state.
print("\nDEFECT TRIAGE")
for defect in defects:
    triage(defect)
    print(f"Defect {defect.id}: {defect.severity}, {defect.priority}")

# Select the keyboard defect for the simulated repair.
keyboard_defect = next(
    defect for defect in defects
    if defect.title == "Button is reachable by keyboard"
)

# Simulate work starting, a change to the model, and readiness for retesting.
keyboard_defect.move_to(DefectStatus.IN_PROGRESS)
page["button_keyboard_reachable"] = True
keyboard_defect.move_to(DefectStatus.READY_FOR_RETEST)

# Run the checks again and select the result relevant to this defect.
# The alternative-text issue remains unresolved.
retest = next(
    result for result in run_accessibility_tests(page)
    if result.name == keyboard_defect.title
)

# Close the defect after a passing retest, or reopen it after a failure.
if retest.passed:
    keyboard_defect.move_to(DefectStatus.CLOSED)
else:
    keyboard_defect.move_to(DefectStatus.REOPENED)

# Display both reports with their current statuses and transition histories.
# Original failure evidence remains unchanged after the keyboard repair.
print("\nDEFECT REPORTS")
for defect in defects:
    print_report(defect)

print("\nRetest result:", "PASS" if retest.passed else "FAIL")