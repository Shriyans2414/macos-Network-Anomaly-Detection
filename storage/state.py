# storage/state.py

import json
from pathlib import Path

STATE_FILE = Path("storage/state.json")

def write_state(data: dict):
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)

def read_state():
    if not STATE_FILE.exists():
        return {
            "status": "TRAINING",
            "score": None,
            "features": {},
            "timestamp": None
        }

    with open(STATE_FILE, "r") as f:
        return json.load(f)
