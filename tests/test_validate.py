"""Pytest suite for scripts/validate_schedule.py.

Covers one fully passing schedule and one case for each failure type:
unknown volunteer, unavailable day, availability window not covering the
shift, double booking within one shift, overlapping shifts on the same day,
skill mismatch, and over-capacity.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from validate_schedule import (  # noqa: E402
    covers,
    parse_time_range,
    skills_match,
    validate,
)

VOLUNTEERS = [
    {
        "name": "Aarav Sharma",
        "skills": "Registration, Check-in, Fluent Hindi/English",
        "availability_sat": "09:00-14:00",
        "availability_sun": "09:00-13:00",
    },
    {
        "name": "Rohan Gupta",
        "skills": "Tech Support, WiFi Troubleshooting, Git",
        "availability_sat": "11:00-18:00",
        "availability_sun": "09:00-17:00",
    },
    {
        "name": "Neha Saxena",
        "skills": "Stage Coordination, Speaker Liaison",
        "availability_sat": "09:00-15:00",
        "availability_sun": "09:00-14:00",
    },
    {
        "name": "Kavita Mishra",
        "skills": "Registration, Kit Handout, Crowd Flow",
        "availability_sat": "Not Available",
        "availability_sun": "09:00-13:00",
    },
]

EVENT = {
    "shift_windows": {
        "Saturday": [
            {"id": "SAT-MORNING", "time": "09:00 - 13:00"},
            {"id": "SAT-AFTERNOON", "time": "13:00 - 17:00"},
        ],
        "Sunday": [
            {"id": "SUN-MORNING", "time": "09:00 - 13:00"},
        ],
    }
}

# Overlapping windows on one day, to exercise the overlap rule.
EVENT_OVERLAPPING = {
    "shift_windows": {
        "Saturday": [
            {"id": "SAT-EARLY", "time": "09:00 - 13:00"},
            {"id": "SAT-MIDDAY", "time": "12:00 - 16:00"},
        ],
    }
}


def make_schedule(assignments, required=1):
    """assignments: list of (shift_id, role, [names])."""
    shifts = {}
    for shift_id, role, names in assignments:
        shifts.setdefault(shift_id, {"slot": shift_id})
        shifts[shift_id][role] = {"required": required, "assigned": list(names), "pending": []}
    return {"status": "draft", "last_updated": "2026-11-07T00:00:00Z", "shifts": shifts, "change_log": []}


def only_issue_kind(issues, keyword):
    matches = [i for i in issues if keyword in i]
    assert matches, f"Expected an issue containing '{keyword}', got: {issues}"
    return matches


# ---------------------------------------------------------------- passing

def test_passing_schedule():
    schedule = make_schedule([
        ("SAT-MORNING", "Registration & Check-in", ["Aarav Sharma"]),
        ("SAT-AFTERNOON", "Tech Support & Network", ["Rohan Gupta"]),
        ("SUN-MORNING", "Stage & Audio/Visual", ["Neha Saxena"]),
    ])
    assert validate(schedule, VOLUNTEERS, EVENT) == []


# ------------------------------------------------------------- failures

def test_unknown_volunteer_rejected():
    schedule = make_schedule([
        ("SAT-MORNING", "Registration & Check-in", ["Ghost Person"]),
    ])
    issues = validate(schedule, VOLUNTEERS, EVENT)
    only_issue_kind(issues, "not in volunteers.csv")


def test_unavailable_day_rejected():
    schedule = make_schedule([
        ("SAT-MORNING", "Registration & Check-in", ["Kavita Mishra"]),  # sat: Not Available
    ])
    issues = validate(schedule, VOLUNTEERS, EVENT)
    only_issue_kind(issues, "Availability")


def test_availability_window_too_late_rejected():
    schedule = make_schedule([
        ("SAT-MORNING", "Tech Support & Network", ["Rohan Gupta"]),  # sat from 11:00, shift 09:00-13:00
    ])
    issues = validate(schedule, VOLUNTEERS, EVENT)
    only_issue_kind(issues, "Availability")


def test_double_booking_within_shift_rejected():
    schedule = make_schedule([
        ("SAT-MORNING", "Registration & Check-in", ["Aarav Sharma"]),
        ("SAT-MORNING", "Help Desk & FAQ", ["Aarav Sharma"]),
    ])
    issues = validate(schedule, VOLUNTEERS, EVENT)
    only_issue_kind(issues, "Double booking")


def test_overlapping_shifts_same_day_rejected():
    schedule = make_schedule([
        ("SAT-EARLY", "Registration & Check-in", ["Aarav Sharma"]),
        ("SAT-MIDDAY", "Registration & Check-in", ["Aarav Sharma"]),  # 12:00-16:00 overlaps 09:00-13:00
    ])
    issues = validate(schedule, VOLUNTEERS, EVENT_OVERLAPPING)
    only_issue_kind(issues, "Overlap")


def test_adjacent_shifts_same_day_allowed():
    fullday = {
        "name": "Full-Day Volunteer",
        "skills": "Registration, Check-in",
        "availability_sat": "09:00-17:00",
        "availability_sun": "Not Available",
    }
    schedule = make_schedule([
        ("SAT-MORNING", "Registration & Check-in", ["Full-Day Volunteer"]),
        ("SAT-AFTERNOON", "Registration & Check-in", ["Full-Day Volunteer"]),  # 09-13 then 13-17: no overlap
    ])
    assert validate(schedule, VOLUNTEERS + [fullday], EVENT) == []


def test_skill_mismatch_rejected():
    schedule = make_schedule([
        ("SAT-MORNING", "Tech Support & Network", ["Aarav Sharma"]),  # registration skills, tech role
    ])
    issues = validate(schedule, VOLUNTEERS, EVENT)
    only_issue_kind(issues, "Skill mismatch")


def test_over_capacity_rejected():
    schedule = make_schedule([
        ("SAT-MORNING", "Registration & Check-in", ["Aarav Sharma", "Kavita Mishra"]),
    ], required=1)
    issues = validate(schedule, VOLUNTEERS, EVENT)
    only_issue_kind(issues, "Over-capacity")


def test_unknown_shift_id_rejected():
    schedule = make_schedule([
        ("FOG-NOON", "Registration & Check-in", ["Aarav Sharma"]),
    ])
    issues = validate(schedule, VOLUNTEERS, EVENT)
    only_issue_kind(issues, "event.json")


# ----------------------------------------------------------- unit pieces

def test_parse_time_range_handles_csv_and_event_formats():
    assert parse_time_range("09:00 - 13:00") == (540, 780)
    assert parse_time_range("09:00-14:00") == (540, 840)
    assert parse_time_range("Not Available") is None
    assert parse_time_range("") is None


def test_covers_requires_full_coverage():
    assert covers((540, 840), (540, 780))       # 09:00-14:00 covers 09:00-13:00
    assert not covers((660, 840), (540, 780))   # 11:00 start misses 09:00
    assert not covers((540, 720), (540, 780))   # ends 12:00, shift ends 13:00


def test_skills_match_keyword_map():
    assert skills_match("Registration, Check-in", "Registration & Check-in")
    assert skills_match("Tech Support, WiFi", "Tech Support & Network")
    assert not skills_match("Registration, Check-in", "Tech Support & Network")
    assert skills_match("Anything", "Mystery Role")  # unmapped role accepts anyone


# ----------------------------------------------------------- demo fixture tests

def test_demo_failing_fixture_detected():
    """Scene 3 failing fixture: Aarav Sharma in SAT-AFTERNOON fails availability."""
    import csv
    import json
    base_dir = Path(__file__).resolve().parents[1]
    with open(base_dir / "data" / "volunteers.csv", "r", encoding="utf-8", newline="") as f:
        volunteers = list(csv.DictReader(f))
    with open(base_dir / "data" / "event.json", "r", encoding="utf-8") as f:
        event = json.load(f)
    with open(base_dir / "demo" / "fixtures" / "scene_3_failing.json", "r", encoding="utf-8") as f:
        schedule = json.load(f)

    issues = validate(schedule, volunteers, event)
    assert len(issues) == 1
    assert "Availability: 'Aarav Sharma'" in issues[0]
    assert "cannot cover SAT-AFTERNOON" in issues[0]


def test_demo_fixed_fixture_passes():
    """Scene 3 fixed fixture: Divya Rawat in SAT-AFTERNOON passes validation."""
    import csv
    import json
    base_dir = Path(__file__).resolve().parents[1]
    with open(base_dir / "data" / "volunteers.csv", "r", encoding="utf-8", newline="") as f:
        volunteers = list(csv.DictReader(f))
    with open(base_dir / "data" / "event.json", "r", encoding="utf-8") as f:
        event = json.load(f)
    with open(base_dir / "demo" / "fixtures" / "scene_3_fixed.json", "r", encoding="utf-8") as f:
        schedule = json.load(f)

    issues = validate(schedule, volunteers, event)
    assert issues == []
