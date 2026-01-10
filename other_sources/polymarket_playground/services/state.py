import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

STATE_FILE = "data/pipeline_state.json"


def _load_state() -> Dict[str, Any]:
    if not os.path.exists(STATE_FILE):
        return {
            "last_run": {
                "snapshot": None,
                "ingestion": None,
                "aggregation": None,
                "analysis": None,
            },
            "stats": {},
            "current_phase": "Idle",
        }
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"last_run": {}, "stats": {}, "current_phase": "Idle"}


def _save_state(state: Dict[str, Any]):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def update_stage_completion(stage_key: str, stats: Optional[Dict] = None):
    """
    Updates the completion timestamp for a specific stage (snapshot, ingestion, aggregation, analysis).
    Optionally updates global stats.
    """
    state = _load_state()
    state["last_run"][stage_key] = datetime.utcnow().isoformat() + "Z"
    if stats:
        # Merge stats
        current_stats = state.get("stats", {})
        current_stats.update(stats)
        state["stats"] = current_stats

    _save_state(state)


def get_pipeline_state() -> Dict[str, Any]:
    return _load_state()


def set_current_phase(phase_name: str):
    state = _load_state()
    state["current_phase"] = phase_name
    _save_state(state)
