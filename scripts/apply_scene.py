#!/usr/bin/env python3
"""Apply a demo scene fixture to data/schedule.json.

Usage:
    python scripts/apply_scene.py 0         # Scene 0: clean reset (empty roster)
    python scripts/apply_scene.py 1         # Scene 1: morning roster proposal (6 filled)
    python scripts/apply_scene.py 2         # Scene 2: Rohan shift modification (7 filled)
    python scripts/apply_scene.py 3         # Scene 3: failing state (Aarav in afternoon)
    python scripts/apply_scene.py 3-fixed   # Scene 3: resolved state (Divya in afternoon)
    python scripts/apply_scene.py 4         # Scene 4: extended afternoon roster (11 filled)
    python scripts/apply_scene.py 5         # Scene 5: confirmed schedule
"""

import shutil
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

SCENE_MAP = {
    "0": "scene_0_clean.json",
    "clean": "scene_0_clean.json",
    "reset": "scene_0_clean.json",
    "1": "scene_1_proposal.json",
    "2": "scene_2_swap.json",
    "3": "scene_3_failing.json",
    "3-fail": "scene_3_failing.json",
    "3-failing": "scene_3_failing.json",
    "3-fixed": "scene_3_fixed.json",
    "3-fix": "scene_3_fixed.json",
    "4": "scene_4_announcement.json",
    "5": "scene_5_confirmed.json",
}


def apply_scene(scene_key):
    base_dir = Path(__file__).resolve().parent.parent
    fixtures_dir = base_dir / "demo" / "fixtures"
    target_path = base_dir / "data" / "schedule.json"

    key = str(scene_key).strip().lower()
    fixture_file = SCENE_MAP.get(key)
    if not fixture_file:
        print(f"[!] Unknown scene '{scene_key}'. Available choices: {', '.join(sorted(SCENE_MAP.keys()))}")
        return 1

    source_path = fixtures_dir / fixture_file
    if not source_path.exists():
        print(f"[!] Fixture file not found: {source_path}")
        return 1

    shutil.copyfile(source_path, target_path)
    print(f"[OK] Applied {fixture_file} -> {target_path}")
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/apply_scene.py <scene_number>")
        print("Choices: 0 (reset), 1, 2, 3 (failing), 3-fixed, 4, 5")
        return 1
    return apply_scene(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
