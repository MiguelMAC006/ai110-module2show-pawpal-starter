from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskType(str, Enum):
    FEEDING = "feeding"
    WALKING = "walking"
    GROOMING = "grooming"
    VET = "vet"
    MEDICATION = "medication"
    PLAYTIME = "playtime"
    OTHER = "other"


@dataclass
class Pet:
    name: str
    species: str
    age: int
    medical_notes: list[str] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def get_profile(self) -> dict:
        """Return a summary dict of all pet attributes."""
        return {
            "name": self.name,
            "species": self.species,
            "age": self.age,
            "medical_notes": self.medical_notes,
            "preferences": self.preferences,
        }

    def update_preferences(self, preferences: dict) -> None:
        """Merge new key/value pairs into the pet's preferences."""
        self.preferences.update(preferences)

    def add_medical_note(self, note: str) -> None:
        """Append a timestamped medical note to the pet's records."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.medical_notes.append(f"[{timestamp}] {note}")


@dataclass
class Task:
    title: str
    task_type: TaskType
    duration: int  # in minutes
    priority: Priority
    due_time: datetime
    pet: Optional["Pet"] = None
    completed: bool = False
    frequency: Optional[str] = None  # "daily", "weekly", or None

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed.

        If the task has a frequency of 'daily' or 'weekly', a new Task instance
        is returned representing the next occurrence. Returns None otherwise.
        """
        self.completed = True
        if self.frequency == "daily":
            return Task(
                title=self.title,
                task_type=self.task_type,
                duration=self.duration,
                priority=self.priority,
                due_time=self.due_time + timedelta(days=1),
                pet=self.pet,
                frequency=self.frequency,
            )
        if self.frequency == "weekly":
            return Task(
                title=self.title,
                task_type=self.task_type,
                duration=self.duration,
                priority=self.priority,
                due_time=self.due_time + timedelta(weeks=1),
                pet=self.pet,
                frequency=self.frequency,
            )
        return None

    def update_priority(self, priority: Priority) -> None:
        """Update the task's priority level."""
        self.priority = priority

    def reschedule(self, new_due_time: datetime) -> None:
        """Move the task's due time to a new datetime."""
        self.due_time = new_due_time


class Owner:
    def __init__(self, name: str, time_available: int, preferences: Optional[dict] = None):
        self.name = name
        self.time_available = time_available  # in minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's list of pets."""
        self.pets.append(pet)

    def add_task(self, task: Task) -> None:
        """Add a task to the owner's task list."""
        self.tasks.append(task)

    def view_tasks(self) -> list[Task]:
        """Return all tasks belonging to the owner."""
        return self.tasks

    def update_availability(self, time_available: int) -> None:
        """Update the number of minutes the owner has available today."""
        self.time_available = time_available

    def get_all_pet_tasks(self) -> list[Task]:
        """Return all tasks that are linked to any of the owner's pets."""
        return [t for t in self.tasks if t.pet in self.pets]


class Scheduler:
    def __init__(self, plan_date: date, owner: Owner):
        """Initialize the scheduler for a specific owner and date."""
        self.date = plan_date
        self.owner = owner
        self.scheduled_tasks: list[Task] = []
        self.explanation: str = ""

    @property
    def total_time(self) -> int:
        """Compute total scheduled time in minutes from scheduled tasks."""
        return sum(t.duration for t in self.scheduled_tasks)

    def generate_plan(self) -> None:
        """Build a schedule from the owner's tasks, sorted by priority and due time, within the available time budget."""
        self.scheduled_tasks = []

        eligible = [
            t for t in self.owner.tasks
            if not t.completed and t.due_time.date() == self.date
        ]
        # Sort HIGH → MEDIUM → LOW, then by due_time within each group
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        eligible.sort(key=lambda t: (priority_order[t.priority], t.due_time))

        skipped = []
        for task in eligible:
            if self.total_time + task.duration <= self.owner.time_available:
                self.add_scheduled_task(task)
            else:
                skipped.append(task.title)

        self._build_explanation(skipped)

    def add_scheduled_task(self, task: Task) -> None:
        """Append a task to the scheduled list."""
        self.scheduled_tasks.append(task)

    def _build_explanation(self, skipped: list[str]) -> None:
        """Compose a human-readable explanation of how the plan was built."""
        lines = [
            f"Plan for {self.date} — {self.owner.name}",
            f"Available time: {self.owner.time_available} min | Scheduled: {self.total_time} min",
            f"Tasks scheduled: {len(self.scheduled_tasks)}",
        ]
        if skipped:
            lines.append(f"Skipped (time budget exceeded): {', '.join(skipped)}")
        self.explanation = "\n".join(lines)

    def get_explanation(self) -> str:
        """Return the plain-text explanation of the current plan."""
        return self.explanation

    def sort_by_time(self) -> list[Task]:
        """Return scheduled tasks sorted ascending by due time.

        Uses a lambda key on the due_time datetime so tasks display in
        chronological order regardless of the order they were added.
        """
        return sorted(self.scheduled_tasks, key=lambda t: t.due_time)

    def filter_tasks(
        self,
        *,
        pet_name: Optional[str] = None,
        completed: Optional[bool] = None,
    ) -> list[Task]:
        """Return owner tasks filtered by pet name and/or completion status.

        Both filters are optional and can be combined. Passing no arguments
        returns all tasks unmodified.

        Args:
            pet_name: If provided, keep only tasks linked to this pet.
            completed: If provided, keep only tasks whose completed flag matches.
        """
        tasks: list[Task] = self.owner.tasks
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet and t.pet.name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> list[str]:
        """Detect scheduled tasks that share the same exact due time.

        Returns a list of human-readable warning strings. An empty list means
        no conflicts were found. The check uses exact-minute matching, so two
        tasks at 08:00 conflict even if their durations don't overlap.
        """
        warnings: list[str] = []
        seen: dict[datetime, Task] = {}
        for task in self.scheduled_tasks:
            if task.due_time in seen:
                other = seen[task.due_time]
                warnings.append(
                    f"⚠ Conflict: '{task.title}' and '{other.title}' "
                    f"are both due at {task.due_time.strftime('%I:%M %p')}."
                )
            else:
                seen[task.due_time] = task
        return warnings

    def complete_task(self, task: Task) -> None:
        """Mark a task complete and auto-schedule the next occurrence if recurring.

        Calls task.mark_complete(), and if a next-occurrence Task is returned
        (because the task has a daily or weekly frequency), adds it to the
        owner's task list so it will appear in future generated plans.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.owner.add_task(next_task)

    def view_plan(self) -> None:
        """Print a formatted version of today's schedule to the terminal."""
        print(f"\n{'='*50}")
        print(f"  Today's Schedule — {self.date}")
        print(f"  Owner: {self.owner.name}  |  Available: {self.owner.time_available} min")
        print(f"{'='*50}")

        if not self.scheduled_tasks:
            print("  No tasks scheduled.")
        else:
            for i, task in enumerate(self.scheduled_tasks, 1):
                pet_label = f" [{task.pet.name}]" if task.pet else ""
                status = "✓" if task.completed else "○"
                due = task.due_time.strftime("%I:%M %p")
                print(
                    f"  {i}. {status} {task.title}{pet_label}"
                    f" | {task.task_type.value} | {task.priority.value.upper()}"
                    f" | {task.duration} min | due {due}"
                )

        print(f"{'='*50}")
        print(f"  Total time: {self.total_time} min\n")
