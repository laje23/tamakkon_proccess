import functools
import asyncio
import traceback

from utils.response import error_response
from utils.notifiter import send_to_admins
from config.admins import debugger_id
from config.bots import bale_bot


def safe_run(func):
    """
    Decorator برای اجرای امن توابع (async و sync)

    - ارسال خطا برای ادمین
    - نمایش پیام مناسب به کاربر
    """

    # -------------------- ASYNC FUNCTION --------------------
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                # متن مناسب برای کاربر
                user_message = str(e) or "خطای نامشخص رخ داده است"

                # متن کامل برای ادمین (با استک‌تریس)
                admin_message = traceback.format_exc()
                await send_to_admins(
                    f"🚨 خطا در تابع `{func.__name__}`\n\n{admin_message}",
                    debugger_id,
                    bale_bot,
                )

                return error_response(
                    f"❌ Error in {func.__name__} \n\n {str(e)}",
                    user_message
                )

        return async_wrapper

    # -------------------- SYNC FUNCTION --------------------
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)

            except Exception as e:
                user_message = str(e) or "خطای نامشخص رخ داده است"
                admin_message = traceback.format_exc()

                # چون sync هست، ارسال پیام ادمین رو async می‌کنیم
                asyncio.create_task(
                    send_to_admins(
                        f"🚨 خطا در تابع `{func.__name__}`\n\n{admin_message}",
                        debugger_id,
                        bale_bot,
                    )
                )

                return error_response(
                    f"❌ Error in {func.__name__} \n\n {str(e)}",
                    user_message
                )

        return sync_wrapper
