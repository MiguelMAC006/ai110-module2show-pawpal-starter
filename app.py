import streamlit as st
from datetime import datetime, date, time
from pawpal_system import Pet, Task, TaskType, Priority, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session state bootstrap ───────────────────────────────────────────────────
# Streamlit re-runs top-to-bottom on every interaction.
# Storing Owner and Scheduler in session_state lets them survive reruns.
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

# ── Step 1: Create the Owner ──────────────────────────────────────────────────
st.subheader("Owner Setup")

with st.form("owner_form"):
    owner_name = st.text_input("Owner name", value="Alex")
    time_available = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=120
    )
    submitted = st.form_submit_button("Save Owner")

if submitted:
    # If owner already exists, just update availability; don't wipe pets/tasks
    if st.session_state.owner is None:
        st.session_state.owner = Owner(name=owner_name, time_available=int(time_available))
    else:
        st.session_state.owner.name = owner_name
        st.session_state.owner.update_availability(int(time_available))
    st.session_state.scheduler = None  # invalidate cached schedule
    st.success(f"Owner **{owner_name}** saved with {time_available} min available.")

owner: Owner | None = st.session_state.owner

if owner is None:
    st.info("Fill in the Owner Setup form above to get started.")
    st.stop()

st.divider()

# ── Step 2: Add Pets ──────────────────────────────────────────────────────────
st.subheader("Add a Pet")

with st.form("pet_form"):
    pet_name = st.text_input("Pet name", value="Luna")
    species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=3)
    medical_note = st.text_input("Medical note (optional)", value="")
    add_pet_btn = st.form_submit_button("Add Pet")

if add_pet_btn:
    new_pet = Pet(name=pet_name, species=species, age=int(age))
    if medical_note.strip():
        new_pet.add_medical_note(medical_note.strip())
    owner.add_pet(new_pet)
    st.success(f"Added **{pet_name}** the {species}.")

if owner.pets:
    st.markdown("**Current Pets:**")
    for pet in owner.pets:
        profile = pet.get_profile()
        notes = "; ".join(profile["medical_notes"]) or "None"
        st.markdown(
            f"- **{profile['name']}** ({profile['species']}, age {profile['age']}) — Notes: {notes}"
        )
else:
    st.info("No pets yet. Add one above.")

st.divider()

# ── Step 3: Add Tasks ─────────────────────────────────────────────────────────
st.subheader("Add a Task")

pet_names = [p.name for p in owner.pets]

with st.form("task_form"):
    task_title = st.text_input("Task title", value="Morning walk")
    task_type = st.selectbox("Task type", [t.value for t in TaskType])
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=30)
    priority = st.selectbox("Priority", [p.value for p in Priority], index=2)
    due_hour = st.slider("Due time (hour)", 0, 23, 8)
    due_minute = st.selectbox("Due time (minute)", [0, 15, 30, 45])
    frequency = st.selectbox("Recurrence", ["None", "daily", "weekly"])
    linked_pet_name = st.selectbox("Link to pet (optional)", ["None"] + pet_names)
    add_task_btn = st.form_submit_button("Add Task")

if add_task_btn:
    due_time = datetime.combine(date.today(), time(due_hour, due_minute))
    linked_pet = next((p for p in owner.pets if p.name == linked_pet_name), None)

    new_task = Task(
        title=task_title,
        task_type=TaskType(task_type),
        duration=int(duration),
        priority=Priority(priority),
        due_time=due_time,
        pet=linked_pet,
        frequency=None if frequency == "None" else frequency,
    )
    owner.add_task(new_task)
    st.session_state.scheduler = None  # invalidate cached schedule
    pet_label = f" for {linked_pet.name}" if linked_pet else ""
    st.success(f"Added task **{task_title}**{pet_label}.")

# ── Filtered task list ────────────────────────────────────────────────────────
if owner.tasks:
    st.markdown("**Current Tasks:**")

    col1, col2 = st.columns(2)
    with col1:
        filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names, key="filter_pet")
    with col2:
        filter_status = st.selectbox(
            "Filter by status", ["All", "Pending", "Done"], key="filter_status"
        )

    # Use Scheduler.filter_tasks() to slice the task list
    _filter_sched = Scheduler(plan_date=date.today(), owner=owner)
    filter_kwargs: dict = {}
    if filter_pet != "All":
        filter_kwargs["pet_name"] = filter_pet
    if filter_status == "Pending":
        filter_kwargs["completed"] = False
    elif filter_status == "Done":
        filter_kwargs["completed"] = True
    filtered = _filter_sched.filter_tasks(**filter_kwargs)

    if filtered:
        rows = []
        for t in filtered:
            rows.append(
                {
                    "Title": t.title,
                    "Type": t.task_type.value,
                    "Priority": t.priority.value,
                    "Duration (min)": t.duration,
                    "Due": t.due_time.strftime("%I:%M %p"),
                    "Recurs": t.frequency or "—",
                    "Pet": t.pet.name if t.pet else "—",
                    "Done": "✓" if t.completed else "○",
                }
            )
        st.table(rows)
    else:
        st.info("No tasks match the current filter.")
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Step 4: Generate Schedule ─────────────────────────────────────────────────
st.subheader("Build Today's Schedule")

if st.button("Generate Schedule"):
    if not owner.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        new_scheduler = Scheduler(plan_date=date.today(), owner=owner)
        new_scheduler.generate_plan()
        st.session_state.scheduler = new_scheduler

scheduler: Scheduler | None = st.session_state.scheduler

if scheduler is not None:
    if not scheduler.scheduled_tasks:
        st.error("No tasks could be scheduled. Check due dates or available time.")
    else:
        st.success(
            f"Scheduled {len(scheduler.scheduled_tasks)} task(s) in {scheduler.total_time} min."
        )

        # ── Conflict warnings ─────────────────────────────────────────────────
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            st.markdown("**⚠ Scheduling conflicts detected — two tasks share the same time slot:**")
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts found.")

        # ── Sorted schedule table (chronological via sort_by_time) ────────────
        st.markdown("**Today's schedule (chronological order):**")
        schedule_rows = []
        for i, t in enumerate(scheduler.sort_by_time(), 1):
            schedule_rows.append(
                {
                    "#": i,
                    "Task": t.title,
                    "Pet": t.pet.name if t.pet else "—",
                    "Type": t.task_type.value,
                    "Priority": t.priority.value.upper(),
                    "Duration": f"{t.duration} min",
                    "Due": t.due_time.strftime("%I:%M %p"),
                    "Recurs": t.frequency or "—",
                }
            )
        st.table(schedule_rows)

        st.markdown("**Plan summary:**")
        st.code(scheduler.get_explanation(), language=None)

        # ── Mark-complete buttons ─────────────────────────────────────────────
        # complete_task() is used (not mark_complete directly) so that recurring
        # tasks automatically get their next occurrence added to the owner's list.
        st.markdown("**Mark tasks complete:**")
        for t in scheduler.scheduled_tasks:
            if not t.completed:
                if st.button(f"✓ Mark '{t.title}' complete", key=f"complete_{t.title}"):
                    scheduler.complete_task(t)
                    st.rerun()
            else:
                recur_note = f" (next {t.frequency} occurrence added)" if t.frequency else ""
                st.markdown(f"~~{t.title}~~ ✓{recur_note}")
