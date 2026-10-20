# testing_lifecycle.py
# Run with: python testing_lifecycle.py
# Describe testing activities and assess sample completion criteria.
# This script reports supplied data; it does not execute tests or archive files.

from dataclasses import dataclass


# Group each phase's name, activities, and expected deliverable.
@dataclass
class Phase:
    name: str
    activities: list[str]
    deliverable: str


# Present a simplified testing lifecycle.
# Activities can overlap or repeat as requirements and software change.
phases = [
    Phase(
        "1. Requirements analysis",
        [
            "Review requirements and acceptance criteria",
            "Identify testable conditions",
            "Clarify missing or conflicting details",
        ],
        "Requirements-to-tests traceability list",
    ),
    Phase(
        "2. Test planning",
        [
            "Set scope and priorities",
            "Choose test types and environment",
            "Define entry, exit, and closure criteria",
        ],
        "Test plan",
    ),
    Phase(
        "3. Test design",
        [
            "Write test cases and test data",
            "Cover normal, boundary, and error paths",
            "Review cases with the team",
        ],
        "Reviewed test cases",
    ),
    Phase(
        "4. Environment setup",
        [
            "Prepare application build and accounts",
            "Load test data",
            "Check that tools and services are available",
        ],
        "Ready test environment",
    ),
    Phase(
        "5. Test execution",
        [
            "Run test cases",
            "Record actual results and evidence",
            "Report defects and retest fixes",
            "Run regression tests",
        ],
        "Execution results and defect reports",
    ),
    Phase(
        "6. Test closure",
        [
            "Check exit criteria",
            "Summarize coverage, results, and open risks",
            "Archive evidence and record lessons learned",
        ],
        "Test closure report",
    ),
]


def completion_decision(results, open_defects):
    # Count planned tests and passing outcomes.
    total = len(results)
    passed = results.count("Pass")

    # Treat every value other than Not Run as executed.
    # This example assumes supplied status values are valid.
    executed = total - results.count("Not Run")

    # Apply the example's completion rules.
    # The pass percentage uses all planned tests as its denominator.
    criteria = {
        "All planned tests executed": executed == total,
        "At least 90% passed": total > 0 and passed / total >= 0.90,

        # Only defects labeled exactly Critical prevent this criterion.
        "No open critical defects": not any(
            defect["severity"] == "Critical"
            for defect in open_defects
        ),

        # Use a placeholder confirmation rather than inspecting an archive.
        "Evidence archived": True,
    }

    return criteria


# Supply ten sample outcomes: eight passes, one failure, and one unrun test.
results = [
    "Pass", "Pass", "Pass", "Pass", "Pass",
    "Pass", "Pass", "Pass", "Fail", "Not Run",
]

# Keep unresolved issues visible even when their severity does not
# directly prevent the no-critical-defects criterion from being met.
open_defects = [
    {
        "id": "BUG-21",
        "severity": "Medium",
        "summary": "Error message is unclear",
    }
]

# Display the activities and deliverable associated with each phase.
print("TESTING LIFE CYCLE")
for phase in phases:
    print(f"\n{phase.name}")
    for activity in phase.activities:
        print(f"- {activity}")
    print("Deliverable:", phase.deliverable)

# Evaluate the sample outcomes against the completion rules.
criteria = completion_decision(results, open_defects)

# Show which conditions are met and which still require attention.
print("\nTEST CLOSURE PLAN")
for criterion, met in criteria.items():
    print(f"{'MET' if met else 'NOT MET'}: {criterion}")

# Summarize the supplied results and unresolved defect count.
print("\nTEST CLOSURE REPORT")
print("Planned tests:", len(results))
print("Passed:", results.count("Pass"))
print("Failed:", results.count("Fail"))
print("Not run:", results.count("Not Run"))
print("Open defects:", len(open_defects))

# Require every modeled criterion before reporting completion.
# The sample remains pending because one test is unrun and only 80% pass.
print("Closure decision:", "COMPLETE" if all(criteria.values()) else "PENDING")