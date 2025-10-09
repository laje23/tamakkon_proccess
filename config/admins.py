import os

debugger_id = os.getenv("DEBUGER_ID")

admins = [
    int(admin_id)
    for admin_id in os.getenv("ADMINS_ID", "").split(",")
    if admin_id.strip()
]
