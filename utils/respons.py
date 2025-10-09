# utils/response.py
import traceback


def success_response(message="", data=None):
    return {"success": True, "message": message, "data": data}


def error_response(message: str, exception: Exception = None):
    return {
        "success": False,
        "message": message,
        "error_type": type(exception).__name__ if exception else None,
        "traceback": traceback.format_exc() if exception else None,
    }
