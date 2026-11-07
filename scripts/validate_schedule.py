#!/usr/bin/env python3
"""Validate schedule.json for capacity, double bookings, availability windows,
skill matches, and overlapping shifts, using event.json and volunteers.csv."""

import csv
import json
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Simple keyword map: a volunteer matches a role when their skills string
# (case-insensitive) contains at least one of the role's keywords.
ROLE_SKILLS = {
    "Registration & Check-in": ["registration", "check-in", "checkin", "kit handout", "crowd flow"],
    "Help Desk & FAQ": ["help desk", "faq", "guidance", "hospitality", "sponsor"],
    "Stage & Audio/Visual": ["stage", "audio", "visual", "anchor", "speaker"],
    "Tech Support & Network": ["tech support", "wifi", "network", "projector", "power", "git", "lab"],
    "Food & Beverage Logistics": ["food", "beverage", "logistics", "inventory", "water station"],
}

DAY_ABBREV = {"Saturday": "sat", "Sunday": "sun", "Friday": "fri", "Monday": "mon"}


def parse_time_range(text):
    """Parse '09:00 - 13:00' or '09:00-14:00' into (start_min, end_min).

    Returns None for blanks and 'Not Available'.
    """
    if not text:
        return None
    cleaned = str(text).strip().lower().replace(" ", "")
    if not cleaned or cleaned in ("notavailable", "na", "-", "n/a"):
        return None
    if "-" not in cleaned:
        return None
    start_s, _, end_s = cleaned.partition("-")
    try:
        return (_to_minutes(start_s), _to_minutes(end_s))
    except ValueError:
        return None


def _to_minutes(hhmm):
    hours, _, minutes = hhmm.partition(":")
    return int(hours) * 60 + int(minutes or "0")


def build_shift_windows(event):
    """Map shift id -> (day, start_min, end_min) from event.json."""
    windows = {}
    for day, shifts in (event.get("shift_windows") or {}).items():
        for shift in shifts:
            rng = parse_time_range(shift.get("time", ""))
            if rng and shift.get("id"):
                windows[shift["id"]] = (day, rng[0], rng[1])
    return windows


def covers(avail_rng, shift_rng):
    """True when the availability window fully covers the shift window."""
    if avail_rng is None or shift_rng is None:
        return False
    return avail_rng[0] <= shift_rng[0] and shift_rng[1] <= avail_rng[1]


def skills_match(volunteer_skills, role_name):
    keywords = ROLE_SKILLS.get(role_name)
    if not keywords:
        return True  # role has no keyword map; accept any volunteer
    skills = (volunteer_skills or "").lower()
    return any(keyword in skills for keyword in keywords)


def validate(schedule, volunteers, event):
    """Return a list of issue strings; empty list means the schedule is valid."""
    issues = []
    known = {v["name"].strip(): v for v in volunteers}
    windows = build_shift_windows(event)

    # Assignments per volunteer for the overlap check:
    # name -> [(day, start_min, end_min, shift_id, role)]
    by_volunteer = {}

    for shift_id, roles in (schedule.get("shifts") or {}).items():
        window = windows.get(shift_id)
        slot_name = roles.get("slot", shift_id)
        seen_in_shift = set()

        if window is None:
            issues.append(f"[!] {shift_id}: No shift window with this id found in event.json shift_windows.")

        for role_name, details in roles.items():
            if role_name == "slot":
                continue

            required = details.get("required", 0)
            assigned = details.get("assigned", [])
            total_required = required
            total_assigned = len(assigned)

            if total_assigned > total_required:
                issues.append(f"[!] {shift_id} [{role_name}]: Over-capacity ({total_assigned}/{total_required} filled).")

            for vol in assigned:
                if vol in seen_in_shift:
                    issues.append(f"[X] Double booking: '{vol}' is assigned to multiple roles in {shift_id} ({slot_name}).")
                else:
                    seen_in_shift.add(vol)

                row = known.get(vol)
                if row is None:
                    issues.append(f"[X] Unknown volunteer: '{vol}' in {shift_id} [{role_name}] is not in volunteers.csv.")
                    continue

                if window is not None:
                    day, shift_start, shift_end = window
                    by_volunteer.setdefault(vol, []).append((day, shift_start, shift_end, shift_id, role_name))

                    abbrev = DAY_ABBREV.get(day, day[:3].lower())
                    avail_col = f"availability_{abbrev}"
                    avail = parse_time_range(row.get(avail_col, ""))
                    if not covers(avail, (shift_start, shift_end)):
                        avail_text = row.get(avail_col, "") or "missing"
                        issues.append(
                            f"[X] Availability: '{vol}' ({avail_text}) cannot cover {shift_id} "
                            f"({slot_name}) on {day}."
                        )

                    if not skills_match(row.get("skills", ""), role_name):
                        issues.append(
                            f"[X] Skill mismatch: '{vol}' assigned to {role_name} in {shift_id} "
                            f"but skills are '{row.get('skills', '')}'."
                        )

    # Cross-shift overlap check: same volunteer, same day, overlapping times.
    for vol, slots in by_volunteer.items():
        ordered = sorted(slots)
        for i, (day1, start1, end1, id1, role1) in enumerate(ordered):
            for day2, start2, end2, id2, role2 in ordered[i + 1:]:
                if day1 == day2 and start1 < end2 and start2 < end1:
                    issues.append(
                        f"[X] Overlap: '{vol}' is in {id1} ({role1}) and {id2} ({role2}), "
                        f"which overlap on {day1}."
                    )

    return issues


def summarize(schedule, issues):
    total_assigned = 0
    total_required = 0
    for roles in (schedule.get("shifts") or {}).items():
        for role_name, details in roles[1].items():
            if role_name == "slot":
                continue
            total_required += details.get("required", 0)
            total_assigned += len(details.get("assigned", []))

    print("=" * 60)
    print("Schedule Validation Report")
    print(f"   Status: {schedule.get('status', 'unknown').upper()}")
    print(f"   Last Updated: {schedule.get('last_updated', 'unknown')}")
    print(f"   Total Filled: {total_assigned} / {total_required} required slots")
    print("=" * 60)

    if issues:
        print("\nFound Issues:")
        for issue in issues:
            print(f"  {issue}")
        return 1
    print("\n[OK] All assignments valid! No conflicts or double-bookings detected.")
    return 0


def main():
    base_dir = Path(__file__).resolve().parent.parent
    schedule_path = base_dir / "data" / "schedule.json"
    volunteers_path = base_dir / "data" / "volunteers.csv"
    event_path = base_dir / "data" / "event.json"

    for path in (schedule_path, volunteers_path, event_path):
        if not path.exists():
            print(f"[!] Error: {path} does not exist.")
            return 1

    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule = json.load(f)
    with open(volunteers_path, "r", encoding="utf-8", newline="") as f:
        volunteers = list(csv.DictReader(f))
    with open(event_path, "r", encoding="utf-8") as f:
        event = json.load(f)

    issues = validate(schedule, volunteers, event)
    return summarize(schedule, issues)


if __name__ == "__main__":
    sys.exit(main())
