import streamlit as st
from datetime import datetime, date, time
from pawpal_system import Pet, Task, TaskType, Priority, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

# ── Session state bootstrap ───────────────────────────────────────────────────
# Streamlit re-runs top-to-bottom on every interaction.
# Storing the Owner in st.session_state means it survives across reruns.
if "owner" not in st.session_state:
    st.session_state.owner = None

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
        st.markdown(f"- **{profile['name']}** ({profile['species']}, age {profile['age']}) — Notes: {notes}")
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

    linked_pet_name = st.selectbox(
        "Link to pet (optional)", ["None"] + pet_names
    )
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
    )
    owner.add_task(new_task)
    pet_label = f" for {linked_pet.name}" if linked_pet else ""
    st.success(f"Added task **{task_title}**{pet_label}.")

if owner.tasks:
    st.markdown("**Current Tasks:**")
    rows = []
    for t in owner.tasks:
        rows.append({
            "Title": t.title,
            "Type": t.task_type.value,
            "Priority": t.priority.value,
            "Duration (min)": t.duration,
            "Due": t.due_time.strftime("%I:%M %p"),
            "Pet": t.pet.name if t.pet else "—",
            "Done": "✓" if t.completed else "○",
        })
    st.table(rows)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Step 4: Generate Schedule ─────────────────────────────────────────────────
st.subheader("Build Today's Schedule")

if st.button("Generate Schedule"):
    if not owner.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler(plan_date=date.today(), owner=owner)
        scheduler.generate_plan()

        if not scheduler.scheduled_tasks:
            st.error("No tasks could be scheduled. Check due dates or available time.")
        else:
            st.success(f"Scheduled {len(scheduler.scheduled_tasks)} task(s) in {scheduler.total_time} min.")

            schedule_rows = []
            for i, t in enumerate(scheduler.scheduled_tasks, 1):
                schedule_rows.append({
                    "#": i,
                    "Task": t.title,
                    "Pet": t.pet.name if t.pet else "—",
                    "Type": t.task_type.value,
                    "Priority": t.priority.value.upper(),
                    "Duration": f"{t.duration} min",
                    "Due": t.due_time.strftime("%I:%M %p"),
                })
            st.table(schedule_rows)

            st.markdown("**Plan summary:**")
            st.code(scheduler.get_explanation(), language=None)

            # Mark-complete buttons
            st.markdown("**Mark tasks complete:**")
            for t in scheduler.scheduled_tasks:
                label = f"✓ Mark '{t.title}' complete"
                if not t.completed:
                    if st.button(label, key=f"complete_{t.title}"):
                        t.mark_complete()
                        st.rerun()
                else:
                    st.markdown(f"~~{t.title}~~ ✓")
