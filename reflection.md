# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My UML design includes four main classes: Pet, Task, Owner, and DailyPlan.

- The Pet class stores information about each pet, including its name, type, medical notes, and preferences. It is responsible for managing pet-specific details.
- The Task class represents individual pet care activities such as feeding, walking, or giving medication. It handles task-related data like priority, duration, and completion status.
- The Owner class represents the user and manages their pets, tasks, availability, and preferences. It acts as the central controller for organizing data.
- The DailyPlan class is responsible for generating a daily schedule of tasks based on constraints like time and priority, and it provides an explanation for the chosen plan.

Together, these classes separate responsibilities clearly: pets hold data, tasks define actions, the owner manages everything, and the daily plan handles scheduling and decision-making.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes—the most significant change was adding pet: Optional[Pet] to Task.

The original UML had no link between Task and Pet. It only connected Task to Owner. During implementation it became clear that a task like "give medication" or "walk" is meaningless without knowing which pet it applies to—generate_plan() couldn't group by pet, and Pet.get_profile() couldn't surface that pet's pending tasks. The relationship was missing from the design but necessary for the logic to work.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two hard constraints and one soft one. First, **time budget**: `generate_plan()` only adds a task if `total_time + task.duration <= owner.time_available`, so the owner is never over-committed. Second, **task date**: only tasks whose `due_time.date()` matches the plan date are eligible — future tasks are ignored automatically. Third, **priority order**: within the budget, tasks are sorted HIGH → MEDIUM → LOW, then by `due_time` within each group, so the most critical care is always attempted first.

Time budget mattered most because the whole purpose of the app is to fit pet care into a busy day. A plan that ignores the owner's availability is useless. Priority was the natural tiebreaker: if not everything fits, the owner should at least know that HIGH-priority items (like medication) were placed before optional enrichment tasks.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The conflict detector uses exact-minute matching: two tasks conflict only if their `due_time` fields are identical down to the minute. It will miss overlapping durations (e.g., a 30-min walk at 08:00 and a 20-min grooming at 08:15 would not be flagged even though they overlap until 08:30).

This is reasonable for a pet-care scheduler because most tasks are not strictly time-blocked—"due at 07:30" means "around 07:30." Exact-time detection catches the clearest double-booking mistakes without requiring the extra complexity of tracking start/end windows for every task. Duration-aware overlap checking would be the logical next step if this evolved into a full calendar tool.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI tools were used across every phase, but with a clear division of labor. During design, I used Copilot Chat to brainstorm which classes should own which responsibilities and to pressure-test the UML — prompting it with "does this relationship make sense given these behaviors?" rather than asking it to generate the diagram outright. During implementation I used inline completions for boilerplate (dataclass fields, enum values, list comprehensions with filters) but wrote the core logic manually. During testing I prompted Copilot Chat with specific edge cases: "what should happen if a pet has no tasks and I call filter_tasks?" to surface test ideas I might have missed. The most effective prompt pattern was giving it a method signature and asking "what are the edge cases for this specific input?" rather than "write tests for my project."

Using separate chat sessions per phase was genuinely useful: the Phase 3 testing chat didn't carry over stale assumptions from earlier phases, so suggestions stayed grounded in the actual current code. Chat mode with `#file` context was best for focused questions; inline completions were best for repetitive boilerplate.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When building `detect_conflicts()`, Copilot suggested comparing tasks pairwise in a nested loop (O(n²)). I recognized that a dictionary keyed on `due_time` would do the same check in a single O(n) pass — one loop, track seen times, emit a warning on the second visit. The AI's version was functionally correct but needlessly slow. I verified my alternative by reasoning through it manually and then confirmed behavior with `test_detect_conflicts_flags_same_due_time`. This was a clear case where accepting the first suggestion would have left an inefficient implementation that I would have had to refactor later.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The 28-test suite covers all four Phase 3 algorithms plus the core model behaviors:

- **sort_by_time**: verified that the returned list is always in ascending `due_time` order, including the edge cases of a single task and an empty schedule.
- **Recurrence**: confirmed that `complete_task()` on a daily task adds a next-day copy, a weekly task adds a next-week copy, and a one-off task adds nothing.
- **Conflict detection**: verified that two tasks at the exact same time produce a warning and that differing times produce none.
- **filter_tasks**: checked filtering by pet name, by completion status, no-tasks empty result, and no-args pass-through.
- **Scheduler core**: time budget enforcement, priority ordering, and skipping already-completed tasks.

These tests mattered because the four algorithmic features are invisible to the user unless they work silently and correctly every time. A bug in recurrence would cause tasks to silently disappear; a bug in conflict detection would let double-bookings through without warning.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

★★★★★ — All 28 tests pass and cover both happy paths and the most important edge cases. Next edge cases to add:

1. **Duration-aware overlap** — two tasks whose time windows overlap but whose `due_time` values differ (currently not detected).
2. **Mixed-frequency recurrence** — completing a daily task inside a plan that also contains weekly tasks, verifying neither interferes with the other.
3. **Owner with zero time available** — `generate_plan()` should schedule nothing and produce an appropriate explanation.
4. **Task linked to a pet not in the owner's pet list** — `get_all_pet_tasks()` should exclude it cleanly.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The recurrence system is the part I'm most satisfied with. The design is clean: `Task.mark_complete()` owns the "create next occurrence" logic and returns it as a value, while `Scheduler.complete_task()` owns the "add it to the owner" side effect. Neither layer knows about the other's internals. That separation made both pieces easy to test in isolation and easy to reason about when debugging.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The conflict detector only catches exact `due_time` matches. A real scheduling tool should detect overlapping duration windows — if a 30-minute walk starts at 08:00 and a 20-minute grooming is due at 08:15, those overlap by 15 minutes even though their start times differ. The fix would require comparing `[due_time, due_time + timedelta(minutes=duration)]` intervals rather than single timestamps. I would also persist data between app sessions (currently everything resets on page refresh) using a JSON file or SQLite.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important insight was that AI tools are most valuable when you already know what you want to build—they accelerate execution, not design. Every time I let AI drive the design (asking "how should I structure this?"), I got plausible but generic answers that I had to throw away once I understood the actual constraints. Every time I arrived at a design decision myself and used AI to fill in the boilerplate, the result fit the system cleanly. Being the lead architect means making the decisions about what matters and why; AI handles the how.
