from datetime import datetime, date
from pawpal_system import Pet, Task, TaskType, Priority, Owner, Scheduler

# ── Pets ──────────────────────────────────────────────────────────────────────
luna = Pet(name="Luna", species="Dog", age=3)
luna.add_medical_note("Allergic to chicken-based food")
luna.update_preferences({"walk_duration": "30 min", "favorite_treat": "peanut butter"})

mochi = Pet(name="Mochi", species="Cat", age=5)
mochi.add_medical_note("Needs dental checkup in April")

# ── Owner ─────────────────────────────────────────────────────────────────────
alex = Owner(name="Alex", time_available=120)  # 2 hours free today
alex.add_pet(luna)
alex.add_pet(mochi)

# ── Tasks added intentionally OUT OF ORDER to test sort_by_time() ─────────────
today = date.today()

luna_grooming = Task(
    title="Brush Luna's coat",
    task_type=TaskType.GROOMING,
    duration=15,
    priority=Priority.LOW,
    due_time=datetime(today.year, today.month, today.day, 18, 0),
    pet=luna,
)

mochi_playtime = Task(
    title="Playtime with Mochi",
    task_type=TaskType.PLAYTIME,
    duration=20,
    priority=Priority.MEDIUM,
    due_time=datetime(today.year, today.month, today.day, 17, 0),
    pet=mochi,
)

# Daily recurring task
luna_feeding = Task(
    title="Feed Luna",
    task_type=TaskType.FEEDING,
    duration=10,
    priority=Priority.HIGH,
    due_time=datetime(today.year, today.month, today.day, 7, 30),
    pet=luna,
    frequency="daily",
)

# Conflict: same time as luna_feeding (07:30) — different pet
mochi_feeding = Task(
    title="Feed Mochi",
    task_type=TaskType.FEEDING,
    duration=5,
    priority=Priority.HIGH,
    due_time=datetime(today.year, today.month, today.day, 7, 30),  # same time → conflict
    pet=mochi,
)

morning_walk = Task(
    title="Morning walk",
    task_type=TaskType.WALKING,
    duration=30,
    priority=Priority.HIGH,
    due_time=datetime(today.year, today.month, today.day, 8, 0),
    pet=luna,
)

alex.add_task(luna_grooming)   # added last, due 18:00
alex.add_task(mochi_playtime)  # added second, due 17:00
alex.add_task(luna_feeding)    # added third, due 07:30
alex.add_task(mochi_feeding)   # added fourth, due 07:30 (conflict!)
alex.add_task(morning_walk)    # added fifth, due 08:00

# ── Generate and display the plan ─────────────────────────────────────────────
scheduler = Scheduler(plan_date=today, owner=alex)
scheduler.generate_plan()
scheduler.view_plan()
print(scheduler.get_explanation())

# ── Step 2: Sort by time ──────────────────────────────────────────────────────
print("\n--- Tasks sorted by due time ---")
for task in scheduler.sort_by_time():
    pet_label = f" [{task.pet.name}]" if task.pet else ""
    print(f"  {task.due_time.strftime('%I:%M %p')}  {task.title}{pet_label}")

# ── Step 2: Filter by pet and by completion status ───────────────────────────
print("\n--- Luna's tasks ---")
for task in scheduler.filter_tasks(pet_name="Luna"):
    status = "done" if task.completed else "pending"
    print(f"  [{status}] {task.title}")

print("\n--- Incomplete tasks ---")
for task in scheduler.filter_tasks(completed=False):
    print(f"  {task.title}")

# ── Step 3: Recurring task demo ───────────────────────────────────────────────
print("\n--- Recurring task: complete 'Feed Luna' (daily) ---")
print(f"  Tasks before: {len(alex.tasks)}")
scheduler.complete_task(luna_feeding)
print(f"  Tasks after:  {len(alex.tasks)}  (next occurrence auto-added)")
next_task = alex.tasks[-1]
print(f"  Next occurrence: '{next_task.title}' due {next_task.due_time.strftime('%Y-%m-%d %I:%M %p')}")

# ── Step 4: Conflict detection ────────────────────────────────────────────────
print("\n--- Conflict detection ---")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")

# ── Pet profiles ──────────────────────────────────────────────────────────────
print("\n--- Pet Profiles ---")
for pet in alex.pets:
    profile = pet.get_profile()
    print(f"\n{profile['name']} ({profile['species']}, age {profile['age']})")
    if profile["medical_notes"]:
        print(f"  Medical notes: {'; '.join(profile['medical_notes'])}")
    if profile["preferences"]:
        print(f"  Preferences:   {profile['preferences']}")
