#!/usr/bin/env python3
"""Inspect schedule.json and volunteers.csv to identify unfilled shifts and
suggest only volunteers who are available for that shift and not already
booked in an overlapping one."""

import csv
import json
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, str(Path(__file__).resolve().parent))

from validate_schedule import (  # noqa: E402
    ROLE_SKILLS,
    build_shift_windows,
    covers,
    parse_time_range,
    skills_match,
)


def load_data(base_dir=None):
    base_dir = Path(base_dir) if base_dir else Path(__file__).resolve().parent.parent
    schedule_path = base_dir / "data" / "schedule.json"
    volunteers_path = base_dir / "data" / "volunteers.csv"
    event_path = base_dir / "data" / "event.json"

    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule = json.load(f)
    with open(volunteers_path, "r", encoding="utf-8", newline="") as f:
        volunteers = list(csv.DictReader(f))
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)
    return schedule, volunteers, event


def booked_names(schedule):
    """Names already assigned or pending in any shift."""
    booked = set()
    for roles in (schedule.get("shifts") or {}).values():
        for role_name, details in roles.items():
            if role_name == "slot":
                continue
            booked.update(details.get("assigned", []))
            booked.update(details.get("pending", []))
    return booked


def suggest_for_shift(schedule, volunteers, windows_by_id, window, role_name, exclude):
    """Volunteers who match the role's skills, are available for the shift's
    exact window, and are not booked in any shift overlapping it."""
    day, shift_start, shift_end = window
    abbrev = {"Saturday": "sat", "Sunday": "sun"}.get(day, day[:3].lower())
    avail_col = f"availability_{abbrev}"
    shift_rng = (shift_start, shift_end)

    # Bookings that overlap this shift on the same day.
    overlapping = set()
    for other_id, other_roles in (schedule.get("shifts") or {}).items():
        other_window = windows_by_id.get(other_id)
        if not other_window or other_window[0] != day:
            continue
        o_start, o_end = other_window[1], other_window[2]
        if o_start < shift_end and shift_start < o_end:
            for role_name2, details in other_roles.items():
                if role_name2 == "slot":
                    continue
                overlapping.update(details.get("assigned", []))
                overlapping.update(details.get("pending", []))

    suggestions = []
    for v in volunteers:
        name = v["name"].strip()
        if name in exclude or name in overlapping:
            continue
        if not skills_match(v.get("skills", ""), role_name):
            continue
        if not covers(parse_time_range(v.get(avail_col, "")), shift_rng):
            continue
        suggestions.append(name)
    return suggestions


def print_gaps():
    schedule, volunteers, event = load_data()
    windows_by_id = build_shift_windows(event)

    print("=" * 65)
    print("UNFILLED SHIFTS & RECOMMENDED CANDIDATES")
    print("=" * 65)

    booked = booked_names(schedule)
    gaps_found = 0

    for shift_id, roles in (schedule.get("shifts") or {}).items():
        slot_label = roles.get("slot", shift_id)
        window = windows_by_id.get(shift_id)
        open_roles = []

        for role_name, details in roles.items():
            if role_name == "slot":
                continue
            required = details.get("required", 0)
            assigned = details.get("assigned", [])
            deficit = required - len(assigned)

            if deficit > 0:
                if window:
                    names = suggest_for_shift(schedule, volunteers, windows_by_id, window, role_name, booked)
                    suggestions = ", ".join(names[:3]) or "No available, unbooked volunteer with matching skills"
                else:
                    suggestions = "Unknown shift id: not in event.json shift_windows"
                open_roles.append({
                    "role": role_name,
                    "deficit": deficit,
                    "suggestions": suggestions,
                })

        if open_roles:
            gaps_found += 1
            print(f"\nShift: {shift_id} - {slot_label}")
            for r in open_roles:
                print(f"   * {r['role']}: Needs {r['deficit']} more volunteer(s)")
                print(f"     Suggested candidates: {r['suggestions']}")

    if gaps_found == 0:
        print("\nAll shifts are currently 100% staffed! No open gaps.")
    print("=" * 65)


if __name__ == "__main__":
    print_gaps()
