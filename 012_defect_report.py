# defect_report.py
# Run with: python defect_report.py

def complete_task(tasks, number):
    # Defect: an invalid task number can select the wrong task.
    tasks[number - 1]["completed"] = True


tasks = [
    {"title": "Write README", "completed": False},
    {"title": "Test the app", "completed": False},
]

try:
    complete_task(tasks, 0)
except Exception as error:
    actual_result = f"{type(error).__name__}: {error}"
else:
    actual_result = f"Task states: {tasks}"


# Prompt engineering techniques used:
# - Assign a clear role.
# - Supply concrete context and reproduction steps.
# - Specify the output format.
# - Require the report to use only observed evidence.
prompt = f"""
You are a software tester writing a defect report.

Context:
A task tracker accepts a task number to mark a task complete.
Task numbers shown to users start at 1.

Steps to reproduce:
1. Start with two incomplete tasks: "Write README" and "Test the app".
2. Call complete_task(tasks, 0).

Expected result:
Reject task number 0. Leave both tasks incomplete.

Actual result:
{actual_result}

Write a defect report with exactly these headings:
Title, Severity, Steps to Reproduce, Expected Result,
Actual Result, Suspected Cause.

Use only the evidence above. Label the cause as suspected,
not confirmed.
""".strip()

print("DEFECT REPORT PROMPT")
print(prompt)