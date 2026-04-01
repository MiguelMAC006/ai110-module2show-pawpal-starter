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

# ── Tasks (all due today) ─────────────────────────────────────────────────────
today = date.today()

morning_walk = Task(
    title="Morning walk",
    task_type=TaskType.WALKING,
    duration=30,
    priority=Priority.HIGH,
    due_time=datetime(today.year, today.month, today.day, 8, 0),
    pet=luna,
)

luna_feeding = Task(
    title="Feed Luna",
    task_type=TaskType.FEEDING,
    duration=10,
    priority=Priority.HIGH,
    due_time=datetime(today.year, today.month, today.day, 7, 30),
    pet=luna,
)

mochi_feeding = Task(
    title="Feed Mochi",
    task_type=TaskType.FEEDING,
    duration=5,
    priority=Priority.HIGH,
    due_time=datetime(today.year, today.month, today.day, 7, 35),
    pet=mochi,
)

mochi_playtime = Task(
    title="Playtime with Mochi",
    task_type=TaskType.PLAYTIME,
    duration=20,
    priority=Priority.MEDIUM,
    due_time=datetime(today.year, today.month, today.day, 17, 0),
    pet=mochi,
)

luna_grooming = Task(
    title="Brush Luna's coat",
    task_type=TaskType.GROOMING,
    duration=15,
    priority=Priority.LOW,
    due_time=datetime(today.year, today.month, today.day, 18, 0),
    pet=luna,
)

alex.add_task(morning_walk)
alex.add_task(luna_feeding)
alex.add_task(mochi_feeding)
alex.add_task(mochi_playtime)
alex.add_task(luna_grooming)

# ── Generate and display the plan ─────────────────────────────────────────────
scheduler = Scheduler(plan_date=today, owner=alex)
scheduler.generate_plan()
scheduler.view_plan()
print(scheduler.get_explanation())

# ── Pet profiles ──────────────────────────────────────────────────────────────
print("\n--- Pet Profiles ---")
for pet in alex.pets:
    profile = pet.get_profile()
    print(f"\n{profile['name']} ({profile['species']}, age {profile['age']})")
    if profile["medical_notes"]:
        print(f"  Medical notes: {'; '.join(profile['medical_notes'])}")
    if profile["preferences"]:
        print(f"  Preferences:   {profile['preferences']}")
