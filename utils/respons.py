# utils/response.py
import json, traceback

STATE_FILE = "schaduler_state.json"

def success_response(message="", data=None):
    return {"success": True, "message": message, "data": data}

def error_response(message: str, exception: Exception = None):
    return {
        "success": False,
        "message": message,
        "error_type": type(exception).__name__ if exception else None,
        "traceback": traceback.format_exc() if exception else None,
    }

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
