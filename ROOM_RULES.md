# Volunteer Desk Room Rules

> **Instructions for the AI Agent and Room Participants**  
> Paste these rules into the room description or pinned message upon setup.

---

### 1. Human Sign-Off Required for All Announcements
* The agent may draft shift rosters, broadcast updates, and announcements in the thread.
* **CRITICAL:** The agent MUST NOT post or finalize any public announcement until the event organiser replies with `"approved"` or `"proceed"`.
* Always include: `"Draft prepared. Awaiting organiser sign-off before publishing."`

### 2. Privacy & Data Protection
* **NEVER** share volunteer personal phone numbers or private contact addresses in room messages or public summaries.
* Refer to volunteers by their full name or registered college email only.
* Treat notes and accommodation requests in `volunteers.csv` with privacy.

### 3. Single Source of Truth
* `data/schedule.json` is the sole source of truth for shift assignments.
* When a volunteer confirms, swaps, or drops a shift in chat, the agent must update `schedule.json` and append an entry to `change_log`.
* Never confirm an assignment in chat without writing it to `schedule.json`.

### 4. Threaded Conversation Protocol
* To keep the main room legible during a busy event:
  * Shift assignment proposals and volunteer banter happen **inside the thread** of the original request.
  * Only finalised daily shift summaries or emergency broadcast alerts may be posted to the top-level channel.
* Keep replies concise, polite, and actionable.

### 5. Conflict Resolution & Capacity
* Do not double-book a volunteer across overlapping shift windows.
* Match volunteer skill tags to role requirements (e.g., Tech Support, Registration, Stage).
* When a gap cannot be filled from available volunteers, flag it explicitly to the organiser with 2 recommended candidates to contact directly.
