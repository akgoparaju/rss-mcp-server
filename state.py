import json
from pathlib import Path

STATE_FILE = Path("app/data.json")
STATE_FILE.parent.mkdir(exist_ok=True, parents=True)

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"entries": [], "read_ids": []}

def save_state(data):
    STATE_FILE.write_text(json.dumps(data, indent=2))

def save_entry_if_unseen(entry):
    state = load_state()
    if entry["id"] not in state["read_ids"] and entry["id"] not in [e["id"] for e in state["entries"]]:
        state["entries"].append(entry)
        save_state(state)

def get_unread():
    state = load_state()
    return [e for e in state["entries"] if e["id"] not in state["read_ids"]]

def mark_all_read():
    state = load_state()
    state["read_ids"].extend(e["id"] for e in state["entries"])
    save_state(state)
