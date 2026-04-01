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

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The conflict detector uses exact-minute matching: two tasks conflict only if their `due_time` fields are identical down to the minute. It will miss overlapping durations (e.g., a 30-min walk at 08:00 and a 20-min grooming at 08:15 would not be flagged even though they overlap until 08:30).

This is reasonable for a pet-care scheduler because most tasks are not strictly time-blocked — "due at 07:30" means "around 07:30." Exact-time detection catches the clearest double-booking mistakes without requiring the extra complexity of tracking start/end windows for every task. Duration-aware overlap checking would be the logical next step if this evolved into a full calendar tool.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
