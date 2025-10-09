import json

STATE_FILE = "schaduler_state.json"


def get_schaduler_state():
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    return data.get("schaduler_state", False)

def set_schaduler_state(value: bool):
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    data["schaduler_state"] = value
    with open(STATE_FILE, "w") as f:
        json.dump(data, f, indent=4)