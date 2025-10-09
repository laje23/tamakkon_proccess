# utils/notifier.py

async def send_to_debugger(result, admin_gruap_id , bot, success=False ):
    target = admin_gruap_id
    message = (
        result.get("message", "پیام نامشخص")
        if isinstance(result, dict)
        else str(result)
    )
    if success or (isinstance(result, dict) and not result.get("success", True)):
        try:
            await bot.send_message(target, message)
        except Exception as e:
            pass
