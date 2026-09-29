# defect_lifecycle.py
# Run with: python defect_lifecycle.py

from dataclasses import dataclass, field
from enum import Enum


class Status(Enum):
    NEW = "New"
    TRIAGED = "Triaged"
    ASSIGNED = "Assigned"
    IN_PROGRESS = "In Progress"
    FIXED = "Fixed"
    RETEST = "Retest"
    CLOSED = "Closed"
    REOPENED = "Reopened"


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


@dataclass
class Defect:
    id: str
    title: str
    steps: list[str]
    expected: str
    actual: str
    severity: str = "Unassigned"  # How much the defect affects the product
    priority: str = "Unassigned"  # How soon the team should fix it
    status: Status = Status.NEW
    assignee: str = ""
    history: list[str] = field(default_factory=list)

    def transition(self, next_status: Status) -> None:
        if next_status not in ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(
                f"Cannot move from {self.status.value} "
                f"to {next_status.value}"
            )

        self.history.append(
            f"{self.status.value} -> {next_status.value}"
        )
        self.status = next_status

    def triage(self, severity: str, priority: str) -> None:
        if severity not in {"Critical", "High", "Medium", "Low"}:
            raise ValueError("Invalid severity")
        if priority not in {"P1", "P2", "P3", "P4"}:
            raise ValueError("Invalid priority")

        self.severity = severity
        self.priority = priority
        self.transition(Status.TRIAGED)

    def assign(self, developer: str) -> None:
        if not developer.strip():
            raise ValueError("Assignee is required")
        self.assignee = developer
        self.transition(Status.ASSIGNED)


def show(defect: Defect) -> None:
    print(f"\n{defect.id}: {defect.title}")
    print("Severity:", defect.severity)
    print("Priority:", defect.priority)
    print("Status:", defect.status.value)
    print("Assignee:", defect.assignee or "None")
    print("Steps:", " -> ".join(defect.steps))
    print("Expected:", defect.expected)
    print("Actual:", defect.actual)
    print("History:", " | ".join(defect.history))


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

# Triage decides severity and priority separately.
defect.triage(
    severity="Critical",
    priority="P1",
)
show(defect)

# Developer workflow.
defect.assign("Developer A")
defect.transition(Status.IN_PROGRESS)
defect.transition(Status.FIXED)
defect.transition(Status.RETEST)

# QA retest fails: reopen the defect.
retest_passed = False
defect.transition(
    Status.CLOSED if retest_passed else Status.REOPENED
)
show(defect)

# Second fix and successful retest.
defect.assign("Developer A")
defect.transition(Status.IN_PROGRESS)
defect.transition(Status.FIXED)
defect.transition(Status.RETEST)
defect.transition(Status.CLOSED)
show(defect)