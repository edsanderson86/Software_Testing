# testing_lifecycle.py
# Run with: python testing_lifecycle.py

from dataclasses import dataclass


@dataclass
class Phase:
    name: str
    activities: list[str]
    deliverable: str


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
    total = len(results)
    passed = results.count("Pass")
    executed = total - results.count("Not Run")

    criteria = {
        "All planned tests executed": executed == total,
        "At least 90% passed": total > 0 and passed / total >= 0.90,
        "No open critical defects": not any(
            defect["severity"] == "Critical"
            for defect in open_defects
        ),
        "Evidence archived": True,
    }

    return criteria


results = [
    "Pass", "Pass", "Pass", "Pass", "Pass",
    "Pass", "Pass", "Pass", "Fail", "Not Run",
]

open_defects = [
    {
        "id": "BUG-21",
        "severity": "Medium",
        "summary": "Error message is unclear",
    }
]

print("TESTING LIFE CYCLE")
for phase in phases:
    print(f"\n{phase.name}")
    for activity in phase.activities:
        print(f"- {activity}")
    print("Deliverable:", phase.deliverable)

criteria = completion_decision(results, open_defects)

print("\nTEST CLOSURE PLAN")
for criterion, met in criteria.items():
    print(f"{'MET' if met else 'NOT MET'}: {criterion}")

print("\nTEST CLOSURE REPORT")
print("Planned tests:", len(results))
print("Passed:", results.count("Pass"))
print("Failed:", results.count("Fail"))
print("Not run:", results.count("Not Run"))
print("Open defects:", len(open_defects))
print("Closure decision:", "COMPLETE" if all(criteria.values()) else "PENDING")