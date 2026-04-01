import pytest
from datetime import datetime, date
from pawpal_system import Pet, Task, TaskType, Priority, Owner, Scheduler


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def sample_pet():
    return Pet(name="Luna", species="Dog", age=3)


@pytest.fixture
def sample_task(sample_pet):
    return Task(
        title="Morning walk",
        task_type=TaskType.WALKING,
        duration=30,
        priority=Priority.HIGH,
        due_time=datetime(2026, 3, 31, 8, 0),
        pet=sample_pet,
    )


@pytest.fixture
def sample_owner():
    return Owner(name="Alex", time_available=120)


# ── Task tests ────────────────────────────────────────────────────────────────

def test_mark_complete_changes_status(sample_task):
    """Calling mark_complete() should flip completed from False to True."""
    assert sample_task.completed is False
    sample_task.mark_complete()
    assert sample_task.completed is True


def test_update_priority(sample_task):
    """update_priority() should change the task's priority."""
    sample_task.update_priority(Priority.LOW)
    assert sample_task.priority == Priority.LOW


def test_reschedule(sample_task):
    """reschedule() should update due_time to the new value."""
    new_time = datetime(2026, 4, 1, 9, 0)
    sample_task.reschedule(new_time)
    assert sample_task.due_time == new_time


# ── Pet tests ─────────────────────────────────────────────────────────────────

def test_add_medical_note_increases_count(sample_pet):
    """add_medical_note() should append an entry to medical_notes."""
    assert len(sample_pet.medical_notes) == 0
    sample_pet.add_medical_note("Allergic to chicken")
    assert len(sample_pet.medical_notes) == 1


def test_add_medical_note_content(sample_pet):
    """The medical note body should appear somewhere in the stored entry."""
    sample_pet.add_medical_note("Needs vaccination")
    assert "Needs vaccination" in sample_pet.medical_notes[0]


def test_update_preferences_merges(sample_pet):
    """update_preferences() should merge new keys without removing existing ones."""
    sample_pet.update_preferences({"treat": "peanut butter"})
    sample_pet.update_preferences({"walk": "30 min"})
    assert sample_pet.preferences["treat"] == "peanut butter"
    assert sample_pet.preferences["walk"] == "30 min"


def test_get_profile_returns_all_fields(sample_pet):
    """get_profile() should return a dict with all expected keys."""
    profile = sample_pet.get_profile()
    for key in ("name", "species", "age", "medical_notes", "preferences"):
        assert key in profile


# ── Owner tests ───────────────────────────────────────────────────────────────

def test_add_pet_increases_count(sample_owner, sample_pet):
    """add_pet() should add the pet to the owner's pets list."""
    assert len(sample_owner.pets) == 0
    sample_owner.add_pet(sample_pet)
    assert len(sample_owner.pets) == 1


def test_add_task_increases_count(sample_owner, sample_task):
    """add_task() should append the task to the owner's task list."""
    assert len(sample_owner.tasks) == 0
    sample_owner.add_task(sample_task)
    assert len(sample_owner.tasks) == 1


def test_update_availability(sample_owner):
    """update_availability() should update the owner's available time."""
    sample_owner.update_availability(60)
    assert sample_owner.time_available == 60


# ── Scheduler tests ───────────────────────────────────────────────────────────

def test_scheduler_total_time_is_zero_when_empty(sample_owner):
    """total_time should be 0 before any tasks are scheduled."""
    scheduler = Scheduler(plan_date=date(2026, 3, 31), owner=sample_owner)
    assert scheduler.total_time == 0


def test_scheduler_respects_time_budget(sample_owner):
    """generate_plan() should not exceed the owner's available time."""
    sample_owner.time_available = 20  # Only 20 min available

    task_a = Task("Feed", TaskType.FEEDING, 10, Priority.HIGH,
                  datetime(2026, 3, 31, 7, 0))
    task_b = Task("Walk", TaskType.WALKING, 30, Priority.HIGH,
                  datetime(2026, 3, 31, 8, 0))  # won't fit

    sample_owner.add_task(task_a)
    sample_owner.add_task(task_b)

    scheduler = Scheduler(plan_date=date(2026, 3, 31), owner=sample_owner)
    scheduler.generate_plan()

    assert scheduler.total_time <= sample_owner.time_available
    assert len(scheduler.scheduled_tasks) == 1


def test_scheduler_skips_completed_tasks(sample_owner, sample_task):
    """generate_plan() should exclude already-completed tasks."""
    sample_task.mark_complete()
    sample_owner.add_task(sample_task)

    scheduler = Scheduler(plan_date=date(2026, 3, 31), owner=sample_owner)
    scheduler.generate_plan()

    assert len(scheduler.scheduled_tasks) == 0


def test_scheduler_sorts_high_priority_first(sample_owner):
    """generate_plan() should place HIGH priority tasks before LOW ones."""
    low_task = Task("Groom", TaskType.GROOMING, 10, Priority.LOW,
                    datetime(2026, 3, 31, 6, 0))
    high_task = Task("Feed", TaskType.FEEDING, 10, Priority.HIGH,
                     datetime(2026, 3, 31, 9, 0))

    sample_owner.add_task(low_task)
    sample_owner.add_task(high_task)

    scheduler = Scheduler(plan_date=date(2026, 3, 31), owner=sample_owner)
    scheduler.generate_plan()

    assert scheduler.scheduled_tasks[0].priority == Priority.HIGH
