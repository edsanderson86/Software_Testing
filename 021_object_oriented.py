# object_oriented_example.py
# Run with: python object_oriented_example.py
# Demonstrate abstraction, inheritance, encapsulation, and polymorphism
# using work and personal tasks.

from abc import ABC, abstractmethod


# Define the shared state and behaviour of all task types.
# This abstract class cannot be instantiated until describe() is implemented.
class Task(ABC):
    def __init__(self, title: str, priority: int):
        # Initialize each task with its own title, priority, and completion state.
        # Type annotations document expected types; they do not enforce them.
        self.title = title

        # A leading underscore signals internal use by convention.
        # It does not prevent access from outside the class.
        self._priority = priority

        # Two leading underscores trigger name mangling to reduce accidental
        # access and naming conflicts; they do not provide strict privacy.
        self.__completed = False

    @property
    def completed(self) -> bool:
        # Expose completion status through a property without a public setter.
        return self.__completed

    def complete(self) -> None:
        # Provide a method for changing the internal completion state.
        self.__completed = True

    def is_high_priority(self) -> bool:
        # Return whether the priority meets this example's threshold.
        return self._priority >= 4

    @abstractmethod
    def describe(self) -> str:
        # Require each concrete subclass to provide its own description.
        pass


# Extend the shared task behaviour with a work-specific project attribute.
class WorkTask(Task):
    def __init__(self, title: str, priority: int, project: str):
        # Initialize inherited attributes before adding project information.
        super().__init__(title, priority)
        self.project = project

    def describe(self) -> str:
        # Implement the abstract method with work-specific details.
        return f"Work task: {self.title} ({self.project})"


# Reuse the same superclass for tasks associated with a personal location.
class PersonalTask(Task):
    def __init__(self, title: str, priority: int, location: str):
        super().__init__(title, priority)
        self.location = location

    def describe(self) -> str:
        # Implement the same method with personal-task details.
        return f"Personal task: {self.title} ({self.location})"


def print_task(task: Task) -> None:
    # Polymorphism selects the object's describe() implementation at runtime.
    # The caller can use either task type through the same interface.
    print(task.describe())


def main() -> None:
    # Demonstrate built-in scalar values and None for an absent value.
    # All values in Python are objects, including strings and numbers.
    title: str = "Write README"
    priority: int = 5
    estimated_hours: float = 1.5
    urgent: bool = True
    missing_due_date = None

    # Use collections to group related values and application settings.
    tags: list[str] = ["documentation", "github"]
    settings: dict[str, bool] = {"notifications": True}

    print("Starting object-oriented example")
    print(title, priority, estimated_hours, urgent, missing_due_date)
    print("Tags:", tags)
    print("Settings:", settings)

    # Create concrete objects with shared behaviour and distinct attributes.
    tasks: list[Task] = [
        WorkTask(title, priority, "Task Tracker"),
        PersonalTask("Buy groceries", 2, "Local shop"),
    ]

    # Process both task types using methods defined by their shared superclass.
    for task in tasks:
        print_task(task)

        # Choose the displayed priority label from the method's Boolean result.
        if task.is_high_priority():
            print("Priority: high")
        else:
            print("Priority: normal")

        # Complete unfinished tasks through the public method.
        if not task.completed:
            task.complete()

        # Read the updated state through the completion property.
        print("Completed:", task.completed)

    # Iterate over the tag collection and display each value.
    for tag in tags:
        print("Tag:", tag)


if __name__ == "__main__":
    # Run the demonstration only when this file is executed directly.
    main()