import json

STATE_FILE = "scheduler_state.json"


def get_scheduler_state():
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    return data.get("scheduler_state", False)


def set_scheduler_state(value: bool):
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    data["scheduler_state"] = value
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=4)
