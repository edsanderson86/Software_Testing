# qa_role_in_agile_scrum.py
# Run with: python qa_role_in_agile_scrum.py

from dataclasses import dataclass, field


@dataclass
class UserStory:
    id: str
    description: str
    acceptance_criteria: list[str]
    test_results: dict[str, bool] = field(default_factory=dict)
    open_defects: list[str] = field(default_factory=list)

    def is_done(self) -> bool:
        return (
            all(
                self.test_results.get(criterion, False)
                for criterion in self.acceptance_criteria
            )
            and not self.open_defects
        )


story = UserStory(
    id="STORY-12",
    description="As a user, I can add a task to my to-do list.",
    acceptance_criteria=[
        "A valid title creates a task",
        "A blank title is rejected",
        "The new task appears in the list",
    ],
)


def add_task(tasks, title):
    title = title.strip()
    if not title:
        return False
    tasks.append(title)
    return True


# Sprint planning: QA reviews the story and turns criteria into tests.
print("SPRINT PLANNING")
print(story.id, story.description)
for criterion in story.acceptance_criteria:
    print("Acceptance criterion:", criterion)


# During the sprint: QA tests the feature as it is developed.
tasks = []
story.test_results["A valid title creates a task"] = add_task(
    tasks, "Write README"
)
story.test_results["A blank title is rejected"] = not add_task(
    tasks, "   "
)
story.test_results["The new task appears in the list"] = (
    "Write README" in tasks
)

print("\nDAILY PROGRESS")
for criterion, passed in story.test_results.items():
    print(f"{'PASS' if passed else 'FAIL'}: {criterion}")


# Example defect found during exploratory testing.
story.open_defects.append(
    "BUG-7: A title containing 500 characters breaks the layout"
)
print("\nEXPLORATORY TESTING")
print("Defect reported:", story.open_defects[0])
print("Story done?", story.is_done())


# Developer fixes the defect; QA retests it.
layout_handles_long_title = True
if layout_handles_long_title:
    story.open_defects.remove(
        "BUG-7: A title containing 500 characters breaks the layout"
    )

print("\nSPRINT REVIEW")
print("Long-title retest:", "PASS" if layout_handles_long_title else "FAIL")
print("Story done?", story.is_done())


# Retrospective: agree on one improvement for the next sprint.
print("\nRETROSPECTIVE")
print("Improvement: include long input values in test design earlier.")