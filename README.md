# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Owner & pet profiles** — Store owner availability and multiple pets with medical notes and preferences.
- **Task management** — Add tasks with type, priority, duration, and due time; link each task to a specific pet.
- **Sorting by time** — The generated schedule is always displayed in chronological order using `Scheduler.sort_by_time()`, so the pet owner sees tasks in the order they need to happen.
- **Priority-aware scheduling** — `generate_plan()` fits tasks within the owner's available time budget, always scheduling HIGH-priority tasks before MEDIUM and LOW.
- **Recurring tasks** — Tasks can be marked `daily` or `weekly`. Completing one automatically queues the next occurrence so nothing falls off the radar.
- **Conflict detection** — `detect_conflicts()` scans the schedule in a single O(n) pass and surfaces a visible `st.warning` whenever two tasks share the exact same time slot.
- **Filtered task view** — `filter_tasks()` lets the owner view tasks by pet name, completion status, or both without touching the schedule.
- **Plain-English plan summary** — `get_explanation()` produces a human-readable summary of what was scheduled, how much time was used, and what was skipped.

## 📸 Demo

<!-- Replace the src paths below with your actual screenshot after running the app -->
<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

## Smarter Scheduling

Phase 3 added four algorithmic improvements to the scheduler:

- **Sort by time** — `Scheduler.sort_by_time()` returns the scheduled task list in ascending chronological order using a `lambda` key on `due_time`, so pet care is always shown in the order it needs to happen.
- **Filter tasks** — `Scheduler.filter_tasks(pet_name=..., completed=...)` lets you slice the owner's task list by pet name, completion status, or both. Useful for viewing only Luna's pending tasks or checking what's already done.
- **Recurring tasks** — `Task` now accepts a `frequency` field (`"daily"` or `"weekly"`). When `Scheduler.complete_task(task)` is called, `mark_complete()` automatically returns a new `Task` shifted forward by `timedelta(days=1)` or `timedelta(weeks=1)`, and the scheduler adds it to the owner's task list so it appears in the next generated plan.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans scheduled tasks for exact `due_time` matches and returns a list of human-readable warning strings. It uses a dictionary keyed on `datetime` for an O(n) single-pass check.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Testing PawPal+

### How to run tests

```bash
python -m pytest
```

Or for verbose output showing each test name:

```bash
python -m pytest -v
```

### What the tests cover

The test suite in `tests/test_pawpal.py` contains **28 tests** across four classes:

| Area | Tests |
|---|---|
| **Task** | `mark_complete`, `update_priority`, `reschedule`, recurrence returns `None` for one-off tasks |
| **Pet** | `add_medical_note`, `update_preferences` merge behavior, `get_profile` keys |
| **Owner** | `add_pet`, `add_task`, `update_availability` |
| **Scheduler** | Time budget enforcement, priority ordering, skips completed tasks, `sort_by_time` (happy path + edge cases), daily/weekly recurrence, conflict detection, `filter_tasks` by pet name and completion status |

Key edge cases verified:
- `sort_by_time` returns `[]` when the schedule is empty
- A pet owner with **no tasks** returns an empty list from `filter_tasks`
- **Two tasks at the exact same time** trigger a conflict warning
- Completing a **one-off task** does not create a follow-up task

### Confidence Level

★★★★★ — All 28 tests pass. The four Phase 3 features (sort, filter, recurrence, conflict detection) are each covered by multiple tests including happy paths and edge cases.
