# qa_role_in_agile_scrum.py
# Run with: python qa_role_in_agile_scrum.py
# Illustrate QA contributions during planning, development, review,
# and retrospective discussions using a small task-creation story.

from dataclasses import dataclass, field


# Keep the story's acceptance criteria, recorded results, and open defects together.
@dataclass
class UserStory:
    id: str
    description: str
    acceptance_criteria: list[str]

    # Give each story independent collections for results and defects.
    test_results: dict[str, bool] = field(default_factory=dict)
    open_defects: list[str] = field(default_factory=list)

    def is_done(self) -> bool:
        # Require a passing result for every criterion and no open defects.
        # Missing results count as failures.
        # This is a simplified completion rule, not a full Definition of Done.
        return (
            all(
                self.test_results.get(criterion, False)
                for criterion in self.acceptance_criteria
            )
            and not self.open_defects
        )


# Describe the user need and the observable outcomes used to assess it.
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
    # Remove surrounding spaces and reject an empty title.
    title = title.strip()
    if not title:
        return False

    # Store a valid title and indicate that creation succeeded.
    tasks.append(title)
    return True


# Sprint planning: review the story and identify testable acceptance criteria.
print("SPRINT PLANNING")
print(story.id, story.description)
for criterion in story.acceptance_criteria:
    print("Acceptance criterion:", criterion)


# During development: exercise valid and invalid task submissions.
tasks = []
story.test_results["A valid title creates a task"] = add_task(
    tasks, "Write README"
)

# A rejected blank submission satisfies this acceptance criterion.
story.test_results["A blank title is rejected"] = not add_task(
    tasks, "   "
)

# Check the stored list as a model of the displayed task list.
# This does not inspect a rendered user interface.
story.test_results["The new task appears in the list"] = (
    "Write README" in tasks
)

# Share current results so the team can see progress and unresolved failures.
print("\nDAILY PROGRESS")
for criterion, passed in story.test_results.items():
    print(f"{'PASS' if passed else 'FAIL'}: {criterion}")


# Exploratory testing: introduce a sample finding beyond the listed criteria.
# The layout defect is illustrative; this script does not reproduce it.
story.open_defects.append(
    "BUG-7: A title containing 500 characters breaks the layout"
)
print("\nEXPLORATORY TESTING")
print("Defect reported:", story.open_defects[0])

# Passing acceptance checks alone do not satisfy this model's completion rule
# while an open defect remains.
print("Story done?", story.is_done())


# Represent a successful long-title retest with a supplied Boolean value.
# A real retest would exercise the repaired layout and inspect its behaviour.
layout_handles_long_title = True
if layout_handles_long_title:
    # Remove the resolved issue from this model's open-defect list.
    # The example does not retain a separate closed-defect history.
    story.open_defects.remove(
        "BUG-7: A title containing 500 characters breaks the layout"
    )

# Sprint review: share the retest outcome and current completion assessment.
print("\nSPRINT REVIEW")
print("Long-title retest:", "PASS" if layout_handles_long_title else "FAIL")
print("Story done?", story.is_done())


# Retrospective: turn the finding into an improvement for future test design.
print("\nRETROSPECTIVE")
print("Improvement: include long input values in test design earlier.")