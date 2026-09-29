# object_oriented_example.py
# Run with: python object_oriented_example.py

from abc import ABC, abstractmethod


# Abstract superclass: defines what every task must be able to do.
class Task(ABC):
    # Parameterized constructor
    def __init__(self, title: str, priority: int):
        self.title = title             # Public attribute
        self._priority = priority      # Protected by convention
        self.__completed = False       # Private via name mangling

    # Encapsulation: controlled access to private data
    @property
    def completed(self) -> bool:
        return self.__completed

    def complete(self) -> None:
        self.__completed = True

    # Method with a return type
    def is_high_priority(self) -> bool:
        return self._priority >= 4

    @abstractmethod
    def describe(self) -> str:
        pass


# Subclass inherits from Task.
class WorkTask(Task):
    def __init__(self, title: str, priority: int, project: str):
        super().__init__(title, priority)
        self.project = project

    def describe(self) -> str:
        return f"Work task: {self.title} ({self.project})"


# Another subclass implements the same method differently.
class PersonalTask(Task):
    def __init__(self, title: str, priority: int, location: str):
        super().__init__(title, priority)
        self.location = location

    def describe(self) -> str:
        return f"Personal task: {self.title} ({self.location})"


def print_task(task: Task) -> None:
    # Polymorphism: the correct describe() runs for each subclass.
    print(task.describe())


def main() -> None:
    # Primitive values
    title: str = "Write README"
    priority: int = 5
    estimated_hours: float = 1.5
    urgent: bool = True
    missing_due_date = None

    # Non-primitive values
    tags: list[str] = ["documentation", "github"]
    settings: dict[str, bool] = {"notifications": True}

    print("Starting object-oriented example")
    print(title, priority, estimated_hours, urgent, missing_due_date)
    print("Tags:", tags)
    print("Settings:", settings)

    # Create objects from classes.
    tasks: list[Task] = [
        WorkTask(title, priority, "Task Tracker"),
        PersonalTask("Buy groceries", 2, "Local shop"),
    ]

    # Loop through objects.
    for task in tasks:
        print_task(task)

        # Conditional logic
        if task.is_high_priority():
            print("Priority: high")
        else:
            print("Priority: normal")

        if not task.completed:
            task.complete()

        print("Completed:", task.completed)

    # Loop through a non-primitive list.
    for tag in tags:
        print("Tag:", tag)


if __name__ == "__main__":
    main()