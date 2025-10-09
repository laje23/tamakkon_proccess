# services/base_service.py
from functools import wraps
from config import bale_bot, eitaa_bot, bale_channel_id, eitaa_channel_id, eitaa_channel_id_test , debugger_id 
from utils import error_response , send_for_amins

# 🔹 دکوریتور try/except برای ایمن کردن اجرای متدها
def safe_execute(func):
    """
    دکوریتور برای اجرای امن متدها.
    هر خطایی که رخ دهد گرفته شده و برمیگرداند.
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            post = error_response(f'error in {func.__name__}' , e)
            return send_for_amins(post ,debugger_id , bale_bot )
    return wrapper


# 🔹 کلاس پایه برای همه سرویس‌ها
class BaseService:
    # بات‌ها و کانال‌های عمومی
    bale_bot = bale_bot
    eitaa_bot = eitaa_bot
    bale_channel_id = bale_channel_id
    eitaa_channel_id = eitaa_channel_id
    eitaa_channel_id_test = eitaa_channel_id_test

    # متد init ساده (مدل‌ها را در کلاس فرزند تعریف می‌کنیم)
    def __init__(self):
        pass
