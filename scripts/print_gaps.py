#!/usr/bin/env python3
"""Inspect schedule.json and volunteers.csv to identify unfilled shifts and suggest eligible volunteers."""

import csv
import json
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def print_gaps():
    base_dir = Path(__file__).resolve().parent.parent
    schedule_path = base_dir / "data" / "schedule.json"
    volunteers_path = base_dir / "data" / "volunteers.csv"

    with open(schedule_path, "r", encoding="utf-8") as f:
        schedule = json.load(f)

    volunteers = []
    with open(volunteers_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            volunteers.append(row)

    print("=" * 65)
    print("UNFILLED SHIFTS & RECOMMENDED CANDIDATES")
    print("=" * 65)

    shifts = schedule.get("shifts", {})
    gaps_found = 0

    for shift_id, roles in shifts.items():
        slot_label = roles.get("slot", shift_id)
        open_roles = []

        for role_name, details in roles.items():
            if role_name == "slot":
                continue
            required = details.get("required", 0)
            assigned = details.get("assigned", [])
            deficit = required - len(assigned)

            if deficit > 0:
                # Find matching candidates from volunteers.csv
                matching_names = []
                for v in volunteers:
                    if any(skill.strip().lower() in role_name.lower() or role_name.lower() in skill.strip().lower() for skill in v["skills"].split(",")):
                        if v["name"] not in assigned:
                            matching_names.append(f"{v['name']} ({v['college'].split()[0]})")

                open_roles.append({
                    "role": role_name,
                    "deficit": deficit,
                    "assigned": assigned,
                    "suggestions": matching_names[:3]
                })

        if open_roles:
            gaps_found += 1
            print(f"\nShift: {shift_id} - {slot_label}")
            for r in open_roles:
                print(f"   * {r['role']}: Needs {r['deficit']} more volunteer(s)")
                if r['suggestions']:
                    print(f"     Suggested candidates: {', '.join(r['suggestions'])}")
                else:
                    print(f"     Suggested: Post open call in room")

    if gaps_found == 0:
        print("\nAll shifts are currently 100% staffed! No open gaps.")
    print("=" * 65)

if __name__ == "__main__":
    print_gaps()
