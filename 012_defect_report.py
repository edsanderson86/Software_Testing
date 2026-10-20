# defect_report.py
# Run with: python defect_report.py
# Reproduce an invalid task-number defect and prepare report details.

def complete_task(tasks, number):
    # Defect: zero becomes index -1, selecting the last task.
    tasks[number - 1]["completed"] = True


# Start with two incomplete tasks so any status change is visible.
tasks = [
    {"title": "Write README", "completed": False},
    {"title": "Test the app", "completed": False},
]

try:
    # Submit an invalid number: displayed task numbers start at 1.
    complete_task(tasks, 0)
except Exception as error:
    # Record the exception if the operation fails.
    actual_result = f"{type(error).__name__}: {error}"
else:
    # Record the task states if the operation finishes without an error.
    actual_result = f"Task states: {tasks}"


# Structure the report details around the reproduction and observed result.
# Keep the suspected explanation separate from the recorded evidence.
report_details = f"""
Title:
Task number 0 completes the last task

Severity:
Proposed: Medium — an invalid task number changes task data.

Steps to Reproduce:
1. Start with two incomplete tasks: "Write README" and "Test the app".
2. Call complete_task(tasks, 0).

Expected Result:
Reject task number 0. Leave both tasks incomplete.

Actual Result:
{actual_result}

Suspected Cause:
Subtracting 1 from task number 0 produces index -1.
Python interprets this index as the last item in the list,
which may explain why the second task is marked complete.
""".strip()

# Display the report for review.
print("DEFECT REPORT")
print(report_details)