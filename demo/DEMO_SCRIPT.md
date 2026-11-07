# Event Volunteer Desk — Demo Walkthrough Script

This script walks through an end-to-end interaction between **Organiser Priya**,
**Volunteer Rohan**, and the **two agents (@volunteer-bot and @roster-checker)**
inside the Switch `#volunteer-desk` room.

Every roster state below was tested with `python scripts/validate_schedule.py`
against `data/volunteers.csv` and `data/event.json`. Each fixture is saved in
`demo/fixtures/` and can be loaded with `python scripts/apply_scene.py <N>`. Run
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
* Aarav Sharma is free 09:00–14:00 — he cannot cover the 13:00–17:00 afternoon shift.
* Divya Rawat is free 13:00–18:00 — she is the ideal Saturday afternoon registration replacement.
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
   Last Updated: 2026-11-14T09:15:00Z
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
   Last Updated: 2026-11-14T09:25:00Z
   Total Filled: 7 / 34 required slots
============================================================

[OK] All assignments valid! No conflicts or double-bookings detected.

Validation passed.
```

---

## Scene 3: Checker Catches an Availability Mistake & Bot Resolves It

**User:** `priya_lead` (Replying in the thread)
```text
@volunteer-bot please add registration coverage for Saturday afternoon (SAT-AFTERNOON 13:00 - 17:00). We want to make sure check-in stays open.
```

**Expected Agent Response:** `@volunteer-bot` (Threaded reply)
```text
Adding Aarav Sharma to SAT-AFTERNOON Registration & Check-in since he handles registration in the morning.

data/schedule.json updated with a change_log entry.

@roster-checker please validate the updated data/schedule.json.
```

**Expected Agent Response:** `@roster-checker` (Threaded reply — REAL failure output)
```text
Ran `python scripts/validate_schedule.py`. Exact output:

============================================================
Schedule Validation Report
   Status: DRAFT
   Last Updated: 2026-11-14T09:35:00Z
   Total Filled: 8 / 34 required slots
============================================================

Found Issues:
  [X] Availability: 'Aarav Sharma' (09:00-14:00) cannot cover SAT-AFTERNOON (Saturday 13:00 - 17:00) on Saturday.

Validation failed.
```

**Expected Agent Response:** `@volunteer-bot` (Threaded reply — revert and smart replacement)
```text
Good catch @roster-checker! Aarav's declared Saturday availability is 09:00-14:00, which leaves at 14:00 and cannot cover the full 13:00-17:00 shift.

I have reverted Aarav Sharma from SAT-AFTERNOON Registration & Check-in and logged the rollback in change_log.

Running `scripts/print_gaps.py` to find eligible, available candidates with Registration skills:
Suggested candidate: Divya Rawat (available 13:00-18:00 on Saturday; note: 'Prefers afternoon on Sat').

I have assigned Divya Rawat to SAT-AFTERNOON Registration & Check-in.
data/schedule.json updated.

@roster-checker please re-validate data/schedule.json.
```

**Expected Agent Response:** `@roster-checker` (Threaded reply — re-check passes)
```text
Ran `python scripts/validate_schedule.py`. Exact output:

============================================================
Schedule Validation Report
   Status: DRAFT
   Last Updated: 2026-11-14T09:37:00Z
   Total Filled: 8 / 34 required slots
============================================================

[OK] All assignments valid! No conflicts or double-bookings detected.

Validation passed.
```

---

## Scene 4: Organiser Extends the Afternoon Roster, Then Asks for the Announcement

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
   Last Updated: 2026-11-14T09:45:00Z
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

## Scene 5: Human-in-the-Loop Sign-Off and Publication

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
   Last Updated: 2026-11-14T10:00:00Z
   Total Filled: 11 / 34 required slots
============================================================

[OK] All assignments valid! No conflicts or double-bookings detected.

Validation passed.
```

---

## Validation Evidence (Tested Against Real Validator)

Every fixture is saved under `demo/fixtures/` and verified with `python scripts/validate_schedule.py`:

| Scene | Fixture File | State | Exit Code | Real Validator Output |
| :--- | :--- | :--- | :--- | :--- |
| **0** | `scene_0_clean.json` | Clean reset (empty) | `0` | `[OK] All assignments valid! 0 / 34` |
| **1** | `scene_1_proposal.json` | SAT-MORNING: 6 assigned | `0` | `[OK] All assignments valid! 6 / 34` |
| **2** | `scene_2_swap.json` | + Rohan in SAT-AFTERNOON Tech | `0` | `[OK] All assignments valid! 7 / 34` |
| **3 (fail)** | `scene_3_failing.json` | + Aarav in SAT-AFTERNOON Reg | `1` | `[X] Availability: 'Aarav Sharma' (09:00-14:00) cannot cover SAT-AFTERNOON` |
| **3 (fixed)**| `scene_3_fixed.json` | Replaced with Divya Rawat | `0` | `[OK] All assignments valid! 8 / 34` |
| **4** | `scene_4_announcement.json` | + Ayush, Zaid, Vikram (11 filled) | `0` | `[OK] All assignments valid! 11 / 34` |
| **5** | `scene_5_confirmed.json` | Status `confirmed`, 11 filled | `0` | `[OK] All assignments valid! 11 / 34` |

Rules kept throughout:
* Rohan Gupta never appears in a shift starting before 11:00 Saturday.
* Aarav Sharma leaves at 14:00, so he cannot cover the 13:00-17:00 shift (caught by the validator in Scene 3).
* No volunteer is in two overlapping shifts; Zaid's back-to-back 09:00-13:00 and 13:00-17:00 shifts are adjacent, not overlapping.
* Every assigned person's skills match their role via the keyword map in `scripts/validate_schedule.py`.
* The announcement names only volunteers present in `schedule.json`; unfilled gaps are stated openly.

## Recording Checklist (Before You Hit Record)

1. `python scripts/reset_demo.py` — restores the clean empty roster (`0 / 34`).
2. Alternatively, use `python scripts/apply_scene.py <scene>` to jump to any scene state:
   * `python scripts/apply_scene.py 0` (clean starting state)
   * `python scripts/apply_scene.py 1` (after Scene 1 proposal)
   * `python scripts/apply_scene.py 2` (after Scene 2 shift swap)
   * `python scripts/apply_scene.py 3` (Scene 3 failing state)
   * `python scripts/apply_scene.py 3-fixed` (Scene 3 resolved state)
   * `python scripts/apply_scene.py 4` (Scene 4 announcement draft)
   * `python scripts/apply_scene.py 5` (Scene 5 confirmed state)
3. Record the five scenes in order; after each bot edit of `data/schedule.json`, wait for the `@roster-checker` validation reply.
4. If a take goes wrong, run `python scripts/reset_demo.py` again.
