import json
from pathlib import Path
from datetime import datetime

# Path where system state is stored
STATE_FILE = Path("storage/state.json")


def write_state(data: dict):
    """
    Persist current detection state to disk.

    Expected keys in `data`:
    - status (NORMAL / ANOMALY / TRAINING)
    - severity (LOW / MEDIUM / HIGH)
    - score (float or None)
    - features (dict)
    - explanations (list of dicts, optional)
    """

    # Ensure required fields exist
    data.setdefault("status", "UNKNOWN")
    data.setdefault("severity", "UNKNOWN")
    data.setdefault("score", None)
    data.setdefault("features", {})
    data.setdefault("explanations", [])

    # Always attach timestamp
    data["timestamp"] = datetime.utcnow().isoformat()

    # Ensure directory exists
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def read_state():
    """
    Read last known detection state.
    Used by /status endpoint and dashboard.
    """

    # Initial state (before any detection)
    if not STATE_FILE.exists():
        return {
            "status": "TRAINING",
            "severity": "UNKNOWN",
            "score": None,
            "features": {},
            "explanations": [],
            "timestamp": None
        }

    with open(STATE_FILE, "r") as f:
        data = json.load(f)

    # Backward compatibility
    data.setdefault("status", "UNKNOWN")
    data.setdefault("severity", "UNKNOWN")
    data.setdefault("score", None)
    data.setdefault("features", {})
    data.setdefault("explanations", [])
    data.setdefault("timestamp", None)

    return data
