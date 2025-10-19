import functools
from utils.response import error_response
from utils.notifiter import send_to_admins
from config.admins import debugger_id
from config.bots import bale_bot
import asyncio


def safe_run(func):
    """
    دکوریتور برای اجرای امن متدها.
    در صورت بروز خطا:
    1. پیام خطا برای ادمین‌ها ارسال می‌شود.
    2. پاسخ استاندارد خطا بازگردانده می‌شود.
    """
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                post = error_response(f"❌ Error in {func.__name__}", e)
                await send_to_admins(
                    f"🚨 خطا در تابع `{func.__name__}`\n\n{str(e)}",
                    debugger_id,
                    bale_bot,
                )
                return post

    else:

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                post = error_response(f"❌ Error in {func.__name__}", e)
                await send_to_admins(
                    f"🚨 خطا در تابع `{func.__name__}`\n\n{str(e)}",
                    debugger_id,
                    bale_bot,
                )
                return post

    return wrapper
