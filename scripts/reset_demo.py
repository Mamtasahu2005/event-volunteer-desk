#!/usr/bin/env python3
"""Restore data/schedule.json to the clean starting state used by the demo.

Run this before recording the demo video so every recording starts from the
same empty roster:
    python scripts/reset_demo.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# The clean starting state: every shift from event.json present, no one
# assigned. Matches the schedule.json committed with the repository.
CLEAN_STATE = {
    "status": "draft",
    "shifts": {
        "SAT-MORNING": {
            "slot": "Saturday 09:00 - 13:00",
            "Registration & Check-in": {"required": 4, "assigned": [], "pending": []},
            "Help Desk & FAQ": {"required": 2, "assigned": [], "pending": []},
            "Stage & Audio/Visual": {"required": 2, "assigned": [], "pending": []},
            "Food & Beverage Logistics": {"required": 3, "assigned": [], "pending": []},
        },
        "SAT-AFTERNOON": {
            "slot": "Saturday 13:00 - 17:00",
            "Registration & Check-in": {"required": 2, "assigned": [], "pending": []},
            "Help Desk & FAQ": {"required": 2, "assigned": [], "pending": []},
            "Tech Support & Network": {"required": 2, "assigned": [], "pending": []},
            "Food & Beverage Logistics": {"required": 3, "assigned": [], "pending": []},
        },
        "SUN-MORNING": {
            "slot": "Sunday 09:00 - 13:00",
            "Help Desk & FAQ": {"required": 2, "assigned": [], "pending": []},
            "Tech Support & Network": {"required": 2, "assigned": [], "pending": []},
            "Stage & Audio/Visual": {"required": 2, "assigned": [], "pending": []},
        },
        "SUN-AFTERNOON": {
            "slot": "Sunday 13:00 - 17:00",
            "Stage & Audio/Visual": {"required": 3, "assigned": [], "pending": []},
            "Food & Beverage Logistics": {"required": 3, "assigned": [], "pending": []},
            "Help Desk & FAQ": {"required": 2, "assigned": [], "pending": []},
        },
    },
    "change_log": [],
}


def reset_demo():
    base_dir = Path(__file__).resolve().parent.parent
    schedule_path = base_dir / "data" / "schedule.json"

    state = {"last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    state.update(CLEAN_STATE)

    with open(schedule_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"[OK] Reset {schedule_path} to the clean demo starting state (all shifts empty).")
    return 0


if __name__ == "__main__":
    sys.exit(reset_demo())
