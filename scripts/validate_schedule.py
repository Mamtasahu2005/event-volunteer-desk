#!/usr/bin/env python3
"""Validate schedule.json for double bookings, over-capacity, and schema consistency."""

import json
import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

def validate():
    base_dir = Path(__file__).resolve().parent.parent
    schedule_path = base_dir / "data" / "schedule.json"

    if not schedule_path.exists():
        print(f"[!] Error: {schedule_path} does not exist.")
        sys.exit(1)

    with open(schedule_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shifts = data.get("shifts", {})
    issues = []
    total_assigned = 0
    total_required = 0

    # Track double-bookings per shift slot
    for shift_id, roles in shifts.items():
        slot_name = roles.get("slot", shift_id)
        volunteers_in_shift = set()

        for role_name, details in roles.items():
            if role_name == "slot":
                continue

            required = details.get("required", 0)
            assigned = details.get("assigned", [])
            total_required += required
            total_assigned += len(assigned)

            # Check capacity
            if len(assigned) > required:
                issues.append(f"[!] {shift_id} [{role_name}]: Over-capacity ({len(assigned)}/{required} filled).")

            # Check for double-booking within the same time window
            for vol in assigned:
                if vol in volunteers_in_shift:
                    issues.append(f"[X] Double booking: '{vol}' is assigned to multiple roles in {shift_id} ({slot_name}).")
                else:
                    volunteers_in_shift.add(vol)

    print("=" * 60)
    print("Schedule Validation Report")
    print(f"   Status: {data.get('status', 'unknown').upper()}")
    print(f"   Last Updated: {data.get('last_updated', 'unknown')}")
    print(f"   Total Filled: {total_assigned} / {total_required} required slots")
    print("=" * 60)

    if issues:
        print("\nFound Issues:")
        for issue in issues:
            print(f"  {issue}")
        sys.exit(1)
    else:
        print("\n[OK] All assignments valid! No conflicts or double-bookings detected.")

if __name__ == "__main__":
    validate()
