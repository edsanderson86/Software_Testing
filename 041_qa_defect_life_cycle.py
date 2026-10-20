# defect_lifecycle.py
# Run with: python defect_lifecycle.py
# Model a defect moving through triage, assignment, repair, and retesting.
# Retest outcomes are supplied examples; no booking tests are executed.

from dataclasses import dataclass, field
from enum import Enum


# Define named lifecycle states to avoid inconsistent status strings.
class Status(Enum):
    NEW = "New"
    TRIAGED = "Triaged"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    FIXED = "Fixed"
    RETEST = "Retest"
    CLOSED = "Closed"
    REOPENED = "Reopened"


# Specify the permitted next states for this example workflow.
# A failed retest returns the defect to assignment for further work.
# Closed is a final state in this model.
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


# Keep reproduction details, classification, ownership, and status together.
@dataclass
class Defect:
    id: str
    title: str
    steps: list[str]
    expected: str
    actual: str
    severity: str = "Unassigned"  # Degree of product impact.
    priority: str = "Unassigned"  # Urgency of repair.
    status: Status = Status.NEW
    assignee: str = ""

    # Give each defect an independent list of recorded transitions.
    history: list[str] = field(default_factory=list)

    def transition(self, next_status: Status) -> None:
        # Reject an unsupported transition before changing status or history.
        if next_status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"Cannot move from {self.status.value} "
                f"to {next_status.value}"
            )

        # Preserve the transition sequence for later review.
        self.history.append(
            f"{self.status.value} -> {next_status.value}"
        )
        self.status = next_status

    def triage(self, severity: str, priority: str) -> None:
        # Validate severity and priority independently.
        if severity not in {"Critical", "High", "Medium", "Low"}:
            raise ValueError("Invalid severity")
        if priority not in {"P1", "P2", "P3", "P4"}:
            raise ValueError("Invalid priority")

        # Store the classification and attempt to advance to Triaged.
        # These fields change before transition validation; an invalid
        # lifecycle call can therefore leave classification changes in place.
        self.severity = severity
        self.priority = priority
        self.transition(Status.TRIAGED)

    def assign(self, developer: str) -> None:
        # Require an assignee containing more than whitespace.
        if not developer.strip():
            raise ValueError("Assignee is required")

        # Store ownership and attempt to advance to Assigned.
        # As with triage, the field changes before transition validation.
        self.assignee = developer
        self.transition(Status.ASSIGNED)


def show(defect: Defect) -> None:
    # Display the current state alongside the original reproduction evidence.
    print(f"\n{defect.id}: {defect.title}")
    print("Severity:", defect.severity)
    print("Priority:", defect.priority)
    print("Status:", defect.status.value)
    print("Assignee:", defect.assignee or "None")
    print("Steps:", " -> ".join(defect.steps))
    print("Expected:", defect.expected)
    print("Actual:", defect.actual)
    print("History:", " | ".join(defect.history))


# Create a new defect from supplied example observations.
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

# Classify impact and repair urgency, then show the triaged report.
defect.triage(
    severity="Critical",
    priority="P1",
)
show(defect)

# Assign ownership and simulate development progressing to a delivered fix.
# Fixed records a claimed repair; Retest indicates verification is next.
defect.assign("Developer A")
defect.transition(Status.IN_PROGRESS)
defect.transition(Status.FIXED)
defect.transition(Status.RETEST)

# Supply a failed retest outcome and reopen the defect.
retest_passed = False
defect.transition(
    Status.CLOSED if retest_passed else Status.REOPENED
)
show(defect)

# Reassign the reopened defect and simulate another repair cycle.
defect.assign("Developer A")
defect.transition(Status.IN_PROGRESS)
defect.transition(Status.FIXED)
defect.transition(Status.RETEST)

# Represent a successful second retest by moving directly to Closed.
# The transition records the outcome without executing a verification check.
defect.transition(Status.CLOSED)
show(defect)