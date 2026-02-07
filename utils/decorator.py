import functools
import asyncio
import traceback
from utils.response import error_response
from utils.notifiter import send_to_admins
from balethon.objects import InlineKeyboard, InlineKeyboardButton
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
                    f"❌ Error in {func.__name__} \n\n {str(e)}", user_message
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
                    f"❌ Error in {func.__name__} \n\n {str(e)}", user_message
                )

        return sync_wrapper


from models.user_permission_model import has_permission
from models import user_model


import inspect
import functools


def require_permission(permission_code: str):
    def decorator(func):

        is_async = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get("user_id")
            if user_id is None:
                raise ValueError("user_id not provided")

            user = user_model.get_user(user_id)
            if not user:
                await bale_bot.send_message(
                    user_id,
                    "کاربر یافت نشد",
                )
                return

            user_db_id = user[0]

            if not has_permission(user_db_id, permission_code):
                await bale_bot.send_message(
                    user_id,
                    "⛔ شما دسترسی انجام این عملیات را ندارید",
                    InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_main")]),
                )
                return

            # 👇 این قسمت مهمه
            if is_async:
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator
