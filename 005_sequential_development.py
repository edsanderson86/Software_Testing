def add_task(tasks, title):
    # Remove surrounding whitespace before validating the title.
    title = title.strip()

    # Reject blank titles before changing the task list.
    if not title:
        raise ValueError("A task needs a title")

    # Add the cleaned title to the supplied list.
    tasks.append(title)


def test_add_task():
    # Start with an empty list to keep the test independent.
    tasks = []

    # Verify that a valid title is saved without surrounding spaces.
    add_task(tasks, "  Write README  ")
    assert tasks == ["Write README"]

    # Verify that a whitespace-only title raises the expected error.
    try:
        add_task(tasks, "   ")
    except ValueError:
        pass
    else:
        # Fail the test if the invalid title was accepted.
        raise AssertionError("A blank title should be rejected")

    # Confirm that the rejected submission left the list unchanged.
    assert tasks == ["Write README"]


if __name__ == "__main__":
    # Run the test when this file is executed directly.
    # The success message appears only if all checks pass.
    test_add_task()
    print("Tests passed")