import functools
from utils import error_response , send_to_admins
from config import bale_bot, debugger_id
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
                    f"🚨 خطا در تابع `{func.__name__}`\n\n{str(e)}" , 
                    debugger_id,
                    bale_bot
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
                f"🚨 خطا در تابع `{func.__name__}`\n\n{str(e)}" , 
                debugger_id,
                bale_bot
            )
                return post

    return wrapper
