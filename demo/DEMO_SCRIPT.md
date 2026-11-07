# Event Volunteer Desk — Demo Walkthrough Script

This script walks through an end-to-end interaction between **Organiser Priya**,
**Volunteer Rohan**, and the **two agents (@volunteer-bot and @roster-checker)**
inside the Switch `#volunteer-desk` room.

Every roster below was checked with `python scripts/validate_schedule.py`
against `data/volunteers.csv` and `data/event.json` — each scene's expected
`schedule.json` state passes validation (evidence at the end). Run
`python scripts/reset_demo.py` before recording so you start from the clean
empty roster.

---

## Persona Setup
* **Account 1 (Organiser):** `priya_lead` (Event Chairperson, HackAvadh 2026)
* **Account 2 (Volunteer):** `rohan_tech` (Student Volunteer, Amity Lucknow)
* **Agent 1:** `@volunteer-bot` — coordinates rosters, edits `data/schedule.json`, drafts announcements
* **Agent 2:** `@roster-checker` — runs `python scripts/validate_schedule.py` and reports the real output

Availability facts used below (from `data/volunteers.csv`):
* Rohan Gupta is free Saturday **from 11:00** — he is never placed in the 9 AM shift.
* Sana Khan is free 10:00–16:00, so she covers no full shift window and is not assigned.
* Saturday shift windows: morning 09:00–13:00, afternoon 13:00–17:00.

---

## Scene 1: Organiser Posts a Staffing Need

**User:** `priya_lead` (Top-level message in `#volunteer-desk`)
```text
@volunteer-bot We have a huge rush expected at check-in on Saturday morning! We need Registration & Check-in staffed (target 4), plus Help Desk, Stage and Food coverage for the 9:00 AM - 1:00 PM shift. Can you check availability and draft a roster?
```

**Expected Agent Response:** `@volunteer-bot` (Threaded reply)
```text
Proposed Shift Roster: SAT-MORNING (09:00 - 13:00)

Based on volunteers.csv availability and skill tags:

Registration & Check-in (2/4 filled):
1. Aarav Sharma (IET Lucknow - Registration, Check-in; available 09:00-14:00)
2. Kavita Mishra (BBDU - Registration, Kit Handout; available 09:00-13:00)

Help Desk & FAQ (1/2 filled):
1. Ananya Singh (IET Lucknow - Help Desk, FAQ; available 08:30-14:00)

Stage & Audio/Visual (2/2 filled):
1. Priya Verma (BBDU - Stage Management, Anchor; available 09:00-18:00)
2. Neha Saxena (IET Lucknow - Stage Coordination, Speaker Liaison; available 09:00-15:00)

Food & Beverage Logistics (1/3 filled):
1. Mohd. Zaid (Integral University - Food Distribution, Logistics; available 09:00-17:00)

Gaps: Registration needs 2 more, Help Desk 1 more, Food 2 more. Divya Rawat
matches Registration but is only available from 13:00, so she cannot take a
morning slot. I have written this roster to data/schedule.json and logged it
in change_log.

Draft prepared. Awaiting organiser sign-off before publishing.

@roster-checker please validate the current data/schedule.json with
python scripts/validate_schedule.py.
```

**Expected Agent Response:** `@roster-checker` (Threaded reply)
```text
Ran `python scripts/validate_schedule.py` in my working directory. Exact output:

============================================================
Schedule Validation Report
   Status: DRAFT
   Last Updated: <timestamp>
   Total Filled: 6 / 34 required slots
============================================================

[OK] All assignments valid! No conflicts or double-bookings detected.

Validation passed.
```

---

## Scene 2: Volunteer Requests a Shift Modification

**User:** `rohan_tech` (Replying in the same thread)
```text
Hey @volunteer-bot, my college lab exam ends at 10:30 am on Saturday, so I won't reach IET campus until 11:00 am. Can I still help? I do tech support.
```

**Expected Agent Response:** `@volunteer-bot` (Threaded reply)
```text
Got it, @rohan_tech! You are not in the 9 AM roster — your declared
availability starts at 11:00, so the morning shift (09:00-13:00) was never
an option for you.

I have assigned you instead to:
* SAT-AFTERNOON, Tech Support & Network (13:00 - 17:00) — inside your
  11:00-18:00 window, and your skill tags match (Tech Support, WiFi
  Troubleshooting, Git).

data/schedule.json updated with a change_log entry. One more Tech Support
slot is still open in that shift.

@roster-checker please validate the updated data/schedule.json.
```

**Expected Agent Response:** `@roster-checker` (Threaded reply)
```text
Ran `python scripts/validate_schedule.py`. Exact output:

============================================================
Schedule Validation Report
   Status: DRAFT
   Last Updated: <timestamp>
   Total Filled: 7 / 34 required slots
============================================================

[OK] All assignments valid! No conflicts or double-bookings detected.

Validation passed.
```

---

## Scene 3: Organiser Extends the Afternoon Roster, Then Asks for the Announcement

**User:** `priya_lead` (Replying in the thread)
```text
@volunteer-bot good. Fill whoever you can into the Saturday afternoon shift as well, then draft the official announcement so volunteers know where to report.
```

**Expected Agent Response:** `@volunteer-bot` (Threaded reply)
```text
SAT-AFTERNOON (13:00 - 17:00) updated:

Registration & Check-in (1/2): Divya Rawat (13:00-18:00; prefers afternoon — matches her note)
Tech Support & Network (2/2): Rohan Gupta, Ayush Srivastava (08:30-17:00)
Food & Beverage Logistics (2/3): Mohd. Zaid, Vikram Patel (11:00-18:00)
Help Desk & FAQ (0/2): no volunteer in volunteers.csv is available for the
full 13:00-17:00 window with Help Desk skills. Ananya leaves at 14:00 and
Sana Khan's window (10:00-16:00) does not cover the shift. Flagging this as
an open gap — recommend an open call in the room.

data/schedule.json updated with a change_log entry.

@roster-checker please validate.
```

**Expected Agent Response:** `@roster-checker` (Threaded reply)
```text
Ran `python scripts/validate_schedule.py`. Exact output:

============================================================
Schedule Validation Report
   Status: DRAFT
   Last Updated: <timestamp>
   Total Filled: 11 / 34 required slots
============================================================

[OK] All assignments valid! No conflicts or double-bookings detected.

Validation passed.
```

**Expected Agent Response:** `@volunteer-bot` (Second reply, after the OK)
```text
Draft Volunteer Shift Announcement (Saturday rosters only — everyone below
is written in data/schedule.json):

> Attention HackAvadh 2026 Volunteers!
>
> Saturday 09:00 - 13:00 (Main Auditorium Entrance, briefing 08:45):
> Registration & Check-in: Aarav Sharma, Kavita Mishra
> Help Desk: Ananya Singh
> Stage & Audio/Visual: Priya Verma, Neha Saxena
> Food & Beverage: Mohd. Zaid
>
> Saturday 13:00 - 17:00:
> Registration & Check-in: Divya Rawat
> Tech Support Hub (Lab Block 2): Rohan Gupta, Ayush Srivastava
> Food & Beverage: Mohd. Zaid, Vikram Patel
>
> Help Desk for the afternoon is still open — DM this channel if you can
> cover 13:00-17:00.

Note: Mohd. Zaid works both shifts; lunch coverage between 13:00 is
handover only. Help Desk afternoon remains a flagged gap.

Draft prepared. Awaiting organiser sign-off before publishing.
```

---

## Scene 4: Human-in-the-Loop Sign-Off and Publication

**User:** `priya_lead`
```text
Approved. Post it to the team!
```

**Expected Agent Response:** `@volunteer-bot`
```text
Announcement published. data/schedule.json status set to "confirmed".
Change log entry appended.

@roster-checker one final validation on the published state, please.
```

**Expected Agent Response:** `@roster-checker`
```text
Ran `python scripts/validate_schedule.py`. Exact output:

============================================================
Schedule Validation Report
   Status: CONFIRMED
   Last Updated: <timestamp>
   Total Filled: 11 / 34 required slots
============================================================

[OK] All assignments valid! No conflicts or double-bookings detected.

Validation passed.
```

---

## Validation Evidence (run before writing this script)

Each scene's expected `schedule.json` state was written to
`data/schedule.json` and checked with the real validator:

| Scene | State | `validate_schedule.py` result |
| :--- | :--- | :--- |
| 1 | SAT-MORNING: 6 volunteers assigned | exit 0 — all assignments valid |
| 2 | + Rohan in SAT-AFTERNOON Tech Support | exit 0 — all assignments valid |
| 3 | + Divya, Ayush, Vikram in SAT-AFTERNOON | exit 0 — all assignments valid |
| 4 | status `confirmed`, no assignment change | exit 0 — all assignments valid |

Notes on rules kept:
* Rohan Gupta never appears in a shift starting before 11:00 Saturday.
* No volunteer is in two overlapping shifts; Zaid's back-to-back 09:00-13:00
  and 13:00-17:00 shifts are adjacent, not overlapping, and both are inside
  his 09:00-17:00 window.
* Every assigned person's skills match their role via the keyword map in
  `scripts/validate_schedule.py`.
* The announcement names only volunteers present in `schedule.json`; unfilled
  gaps are stated as gaps, not hidden.

## Recording Checklist (before you hit record)

1. `python scripts/reset_demo.py` — restores the clean empty roster.
2. `python scripts/validate_schedule.py` — should print `[OK] ... 0 / 34`.
3. Record the four scenes in order; after each bot edit of
   `data/schedule.json`, wait for the `@roster-checker` validation reply.
4. If a take goes wrong, run step 1 again and re-record.
