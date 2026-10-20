# defect_lifecycle.py
# Run with: python defect_lifecycle.py
# Demonstrate reporting, triage, assignment, repair, retesting, and closure.
# The repair and retest outcomes are simulated rather than executed.

from dataclasses import dataclass, field
from enum import Enum


# Define the available lifecycle states using consistent named values.
class Status(Enum):
    NEW = "New"
    TRIAGED = "Triaged"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    FIXED = "Fixed"
    RETEST = "Retest"
    CLOSED = "Closed"
    REOPENED = "Reopened"


# Map each current state to its permitted next states.
# A failed retest leads to reassignment; Closed ends this example workflow.
ALLOWED_TRANSITIONS = {
    Status.NEW: {Status.TRIAGED},
    Status.TRIAGED: {Status.ASSIGNED},
    Status.ASSIGNED: {Status.IN_PROGRESS},
    Status.IN_PROGRESS: {Status.FIXED},
    Status.FIXED: {Status.RETEST},
    Status.RETEST: {Status.CLOSED, Status.REOPENED},
    Status.REOPENED: {Status.ASSIGNED},
    Status.CLOSED: set(),
}


# Store reproduction evidence alongside classification and ownership details.
@dataclass
class Defect:
    id: str
    title: str
    steps: list[str]
    expected: str
    actual: str
    severity: str = "Unassigned"  # How much the defect affects the product.
    priority: str = "Unassigned"  # How urgently the repair should be addressed.
    status: Status = Status.NEW
    assignee: str = ""

    # Give each defect its own transition history.
    history: list[str] = field(default_factory=list)

    def transition(self, next_status: Status) -> None:
        # Check the workflow before changing the current status.
        if next_status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"Cannot move from {self.status.value} "
                f"to {next_status.value}"
            )

        # Record the transition before replacing the current state.
        self.history.append(
            f"{self.status.value} -> {next_status.value}"
        )
        self.status = next_status

    def triage(self, severity: str, priority: str) -> None:
        # Validate impact and urgency as separate classifications.
        if severity not in {"Critical", "High", "Medium", "Low"}:
            raise ValueError("Invalid severity")
        if priority not in {"P1", "P2", "P3", "P4"}:
            raise ValueError("Invalid priority")

        # Save the classification and request the Triaged state.
        # Classification changes occur before transition validation.
        self.severity = severity
        self.priority = priority
        self.transition(Status.TRIAGED)

    def assign(self, developer: str) -> None:
        # Reject an empty or whitespace-only assignee.
        if not developer.strip():
            raise ValueError("Assignee is required")

        # Store the supplied name and request the Assigned state.
        # The assignee changes even if the subsequent transition is rejected.
        self.assignee = developer
        self.transition(Status.ASSIGNED)


def show(defect: Defect) -> None:
    # Display current progress while preserving the original failure evidence.
    print(f"\n{defect.id}: {defect.title}")
    print("Severity:", defect.severity)
    print("Priority:", defect.priority)
    print("Status:", defect.status.value)
    print("Assignee:", defect.assignee or "None")
    print("Steps:", " -> ".join(defect.steps))
    print("Expected:", defect.expected)
    print("Actual:", defect.actual)
    print("History:", " | ".join(defect.history))


# Report a sample booking defect with steps and contrasting outcomes.
defect = Defect(
    id="BUG-42",
    title="Booking succeeds when no seats remain",
    steps=[
        "Open a flight with zero available seats",
        "Enter passenger details",
        "Select Confirm booking",
    ],
    expected="Booking is rejected; available seats remain zero.",
    actual="Booking is confirmed; available seats become negative.",
)

# Triage records the example's impact and repair urgency independently.
defect.triage(
    severity="Critical",
    priority="P1",
)
show(defect)

# Assign the defect and simulate work progressing to a reported fix.
# Move to Retest so the repair can be checked before closure.
defect.assign("Developer A")
defect.transition(Status.IN_PROGRESS)
defect.transition(Status.FIXED)
defect.transition(Status.RETEST)

# Represent a failed first retest and reopen the defect for further work.
retest_passed = False
defect.transition(
    Status.CLOSED if retest_passed else Status.REOPENED
)
show(defect)

# Reassign the reopened defect and repeat the repair workflow.
defect.assign("Developer A")
defect.transition(Status.IN_PROGRESS)
defect.transition(Status.FIXED)
defect.transition(Status.RETEST)

# Represent a successful second retest by closing the defect.
# No test function verifies the repair in this demonstration.
defect.transition(Status.CLOSED)
show(defect)