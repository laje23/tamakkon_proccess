import functools
from balethon.objects import InlineKeyboard, InlineKeyboardButton
from config.bots import bale_bot
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
