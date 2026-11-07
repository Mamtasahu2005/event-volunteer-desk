# Event Volunteer Desk

> A Switch room where an event organiser, student volunteers, and two AI agents plan and staff event shifts together — with a validator agent that checks every roster change before anything is announced.
> *Built for the **Flip the Switch Hackathon** (WeMakeDevs) — Business Workflow track.*

---

## The Problem

I'm a student volunteer in Lucknow, and event teams here coordinate volunteers over messy WhatsApp groups. Organising college hackathons and conferences (like the sample event in this repo, **HackAvadh 2026**) means chasing availability across dozens of chats and spreadsheets:

* Organisers waste hours collecting availability by hand, then build rosters in spreadsheets that are outdated the moment someone's exam schedule changes.
* Last-minute dropouts trigger manual scrambling, and the replacement picked is often someone who is already booked or not actually free.
* Volunteers don't know who to notify when they need to swap a shift.
* Announcements go out with missing coverage, because nothing checks the roster before it is published.

**Event Volunteer Desk** turns a team chat room into an operations desk: one agent proposes and edits the roster in conversation, a second agent independently validates every change by running a real Python script, and nothing is announced until the human organiser approves.

---

## How Switch Is Used

Switch is the core of this project — the whole workflow lives in one Switch room on **Mattermost**:

1. **Room:** the template creates the `volunteer-desk` room and mirrors it to Mattermost via Switch's **bridge**, with the deployer (`{$creator}`) in it.
2. **Two agents:** `volunteer-bot` (addresses `anyone` — organisers and volunteers talk to it) and `roster-checker` (addresses `owner-agents` — it answers agent handoffs).
3. **Handoff between agents:** after every change to `data/schedule.json`, `volunteer-bot` must address `@roster-checker` by name in the thread. roster-checker runs `python scripts/validate_schedule.py` and replies with the validator's exact output — it is instructed never to invent a result.
4. **Room instructions and rules:** `ROOM_RULES.md` ships inside the template itself — as the room's `instructions:` block and as a room document ("Room Rules") created with the room. Nothing needs to be pasted by hand. The rules enforce human sign-off before announcements, volunteer privacy, and `data/schedule.json` as the single source of truth.
5. **Human-in-the-loop gate:** `volunteer-bot` may only draft an announcement after roster-checker reports the schedule is OK **and** the organiser replies "Approved".

```mermaid
flowchart TD
    A["Organiser posts staffing need in Mattermost"] --> B["Switch routes message to @volunteer-bot"]
    B --> C["Agent reads volunteers.csv & event.json"]
    C --> D["Agent proposes roster in thread, writes schedule.json"]
    D --> E["Handoff: @volunteer-bot names @roster-checker"]
    E --> F["roster-checker runs validate_schedule.py, posts real output"]
    F --> G{"Validator OK?"}
    G -- "No (e.g. availability conflict)" --> H["volunteer-bot reverts change, picks replacement with print_gaps.py"]
    H --> D
    G -- "Yes" --> I["Agent drafts announcement (locked)"]
    I --> J{"Organiser replies 'Approved'?"}
    J -- "Yes" --> K["Announcement published, schedule confirmed"]
    J -- "No" --> D
```

---

## Why Two Agents?

Single-agent systems often hallucinate adherence to rules: an agent asked to "check the roster" frequently declares that everything looks fine without verifying constraints.

By splitting operations into two complementary agents with separate addressing scopes in Switch:

1. **`@volunteer-bot` (The Coordinator):**
   * Scope: `anyone`.
   * Role: Listens to the organiser and volunteers, understands conversational shift requests, reads availability and skills, proposes shift allocations, and writes to `data/schedule.json`.
   * Constraint: Forbidden from certifying its own work or broadcasting announcements without approval.
2. **`@roster-checker` (The Auditor):**
   * Scope: `owner-agents`.
   * Role: Activated exclusively via explicit agent handoff (`@roster-checker ...`).
   * Constraint: Forbidden from editing schedules or drafting messages; its sole job is executing `python scripts/validate_schedule.py` and quoting the real terminal output directly into the thread.

This strict separation enforces accountability: a mistake made by the coordinator (such as scheduling a volunteer whose availability window ends early) is immediately caught by the auditor before any human sees an announcement.

---

## Repository Structure
```text
event-volunteer-desk/
├── README.md                      # Project overview, architecture & reproduction steps
├── ROOM_RULES.md                  # Human-readable copy; the rules ship inside the template
├── volunteer-desk.template.yaml   # Switch template: two agents, room, rules, kickoff
├── data/                          # SAMPLE DATA — fictional volunteers and event
│   ├── event.json                 # Event metadata, shift windows & role quotas
│   ├── volunteers.csv             # 12 sample student volunteers with skills & availability
│   └── schedule.json              # Single source of truth for shift allocations
├── scripts/
│   ├── validate_schedule.py       # Checks capacity, double bookings, availability, skills, overlaps
│   ├── print_gaps.py              # Reports unfilled shifts + available, unbooked candidates
│   ├── reset_demo.py              # Restores schedule.json to the clean demo state
│   └── apply_scene.py             # Applies any demo scene fixture to data/schedule.json
├── tests/
│   └── test_validate.py           # pytest suite for the validator and demo fixtures (15 tests)
├── demo/
│   ├── DEMO_SCRIPT.md             # Scene-by-scene recording script, validated per scene
│   └── fixtures/                  # Ground-truth JSON fixtures for scenes 0 through 5
└── docs/
    └── screenshots/               # Walkthrough screenshots for Switch Console and room flow
        └── .gitkeep
```

---

## Run the Checks Yourself

You can clone this repository and reproduce all deterministic validation checks in seconds:

```bash
# 1. Install pytest (if not already installed)
pip install pytest

# 2. Reset schedule to clean starting state
python scripts/reset_demo.py

# 3. Run the validator on the clean schedule (passes with 0/34 filled)
python scripts/validate_schedule.py

# 4. Run the gap finder to inspect open shifts and matching candidate recommendations
python scripts/print_gaps.py

# 5. Run the full pytest test suite (15 tests covering all edge cases and fixtures)
python -m pytest -q

# 6. Witness the real validator catch an availability conflict in Scene 3:
python scripts/apply_scene.py 3
python scripts/validate_schedule.py
# (Fails with: [X] Availability: 'Aarav Sharma' (09:00-14:00) cannot cover SAT-AFTERNOON)

# 7. Apply the fixed Scene 3 state and verify it passes:
python scripts/apply_scene.py 3-fixed
python scripts/validate_schedule.py
# (Passes with: [OK] All assignments valid! 8 / 34 required slots)

# 8. Reset back to clean state when done
python scripts/reset_demo.py
```

---

## Step-by-Step Setup Guide

### 1. Prerequisites
* **Switch Console** ([Download a release](https://github.com/sandbox-quantum/switch/releases))
* **Docker Desktop** (for running the local Switch server + bundled Mattermost)
* **Python 3.10+** (for the validation helpers and tests)
* A coding-agent provider signed in (the template tries **Antigravity** first, then falls back to Claude Code, Codex, or OpenCode)

### 2. Launch the Local Switch Server
1. Start Docker Desktop.
2. Open **Switch Console** and start your local server (Switch Core + the bundled Mattermost on `http://localhost:8000`).
3. Under **Agent Providers**, sign in to the provider you want the agents to run on.

### 3. Create the Room from the Template
1. Clone this repository:
   ```bash
   git clone https://github.com/Mamtasahu2005/event-volunteer-desk
   ```
2. In **Switch Console**, open the **Templates** page and click **Import template**.
3. Choose the `volunteer-desk.template.yaml` file from this repository.
4. Click **Use** and fill the fields:
   * **Event name** — pre-filled with "HackAvadh 2026"; change it to your event.
   * **Repository URL** — pre-filled with this repo; the agents clone it into their working directory so both read and write the same `data/` and `scripts/`.
   * Advanced (folded): provider, machine/location, working directory, and the messaging app (bridge) — defaults pick the first installed provider, this machine, a shared folder under the agents directory, and the server's default app (Mattermost on the bundled server).
5. Click **Create**. Switch creates the `volunteer-desk` room in Mattermost, puts both agents and you in it, installs the room rules, and posts the kickoff (each agent says hello in one line).

---

## Tested vs Untested

* **Tested locally:** validator, gap finder, demo fixtures and pytest suite.
* **Live Switch run on Mattermost:** not recorded for this submission.
* **Untested:** Switch's Slack and Discord bridges should work (the template takes any bridge the server has), but they have not been tried for this project.
* All names, emails, and availability rows in `data/` are **sample data** for the demo, not real volunteers.

---

## How to Run the Demo

Follow the scene-by-scene script in [`demo/DEMO_SCRIPT.md`](demo/DEMO_SCRIPT.md):

1. **Scene 1 (Staffing request):** the organiser asks @volunteer-bot to staff the Saturday morning shift. Bot proposes roster, writes `schedule.json`, hands off to @roster-checker, which validates OK.
2. **Scene 2 (Volunteer shift modification):** volunteer Rohan notes he arrives at 11:00. Bot puts him in afternoon Tech Support and hands off to checker (validates OK).
3. **Scene 3 (Checker catches mistake & bot fixes it):** bot tries adding Aarav Sharma to the afternoon shift. Roster-checker flags availability error. Bot rolls back, runs `print_gaps.py`, assigns Divya Rawat, and re-check passes.
4. **Scene 4 (Afternoon roster extension & announcement draft):** bot finishes filling afternoon shift, notes open Help Desk gap, hands off to checker, and drafts announcement.
5. **Scene 5 (Human-in-the-loop sign-off & publication):** organiser replies "Approved", announcement is published, schedule marked confirmed, with one final validation.

---

## Screenshots & Demo Video

Live Switch run on Mattermost: not recorded for this submission. All core shift-scheduling operations, the two-agent coordinator/checker handoff protocol, gap identification, and deterministic constraint validation rules are fully verified locally via test fixtures and the automated pytest suite.

---

## What I Learned

1. **Rooms beat solo prompts:** an agent embedded in a shared team channel, with the real data files in its working directory, can do operational work that a chat window alone cannot.
2. **A second agent as a checker helps:** making validation a separate agent that must paste real script output (and is forbidden from inventing results) keeps the coordinator agent honest.
3. **Human-in-the-loop safety matters:** requiring explicit organiser approval before any announcement prevented premature or wrong broadcasts during testing.
4. **Deterministic checks + conversation:** keeping `data/schedule.json` as machine-readable ground truth let both the agents and plain Python scripts agree on what is true.

---

## License

[MIT](LICENSE)
