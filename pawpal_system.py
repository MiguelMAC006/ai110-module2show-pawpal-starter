from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    age: int
    medical_notes: list[str] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def get_profile(self) -> dict:
        pass

    def update_preferences(self, preferences: dict) -> None:
        pass

    def add_medical_note(self, note: str) -> None:
        pass


@dataclass
class Task:
    title: str
    task_type: str
    duration: int  # in minutes
    priority: str
    due_time: datetime
    completed: bool = False

    def mark_complete(self) -> None:
        pass

    def update_priority(self, priority: str) -> None:
        pass

    def reschedule(self, new_due_time: datetime) -> None:
        pass


class Owner:
    def __init__(self, name: str, time_available: int, preferences: Optional[dict] = None):
        self.name = name
        self.time_available = time_available  # in minutes
        self.preferences = preferences or {}
        self.pets: list[Pet] = []
        self.tasks: list[Task] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def add_task(self, task: Task) -> None:
        pass

    def view_tasks(self) -> list[Task]:
        pass

    def update_availability(self, time_available: int) -> None:
        pass


class DailyPlan:
    def __init__(self, date: date, owner: Owner):
        self.date = date
        self.owner = owner
        self.scheduled_tasks: list[Task] = []
        self.total_time: int = 0  # in minutes
        self.explanation: str = ""

    def generate_plan(self) -> None:
        pass

    def add_scheduled_task(self, task: Task) -> None:
        pass

    def get_explanation(self) -> str:
        pass

    def view_plan(self) -> None:
        pass
