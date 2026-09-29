def add_task(tasks, title):
    title = title.strip()

    if not title:
        raise ValueError("A task needs a title")

    tasks.append(title)


def test_add_task():
    tasks = []

    add_task(tasks, "  Write README  ")
    assert tasks == ["Write README"]

    try:
        add_task(tasks, "   ")
    except ValueError:
        pass
    else:
        raise AssertionError("A blank title should be rejected")

    assert tasks == ["Write README"]


if __name__ == "__main__":
    test_add_task()
    print("Tests passed")