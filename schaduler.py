import asyncio
from datetime import datetime
from utils.schaduler_utils import get_schaduler_state 
from utils.notifiter import send_to_admins
from pytz import timezone
from services import *


async def scheduled_messages():
    sent_today = set()  # برای اینکه یک پیام دوباره در همون دقیقه ارسال نشه

    while True:
        iran = timezone("Asia/Tehran")
        now = datetime.now(iran)
        current_time = now.strftime("%H:%M")
        if get_schaduler_state():
            if current_time not in sent_today:
                try:
                    if current_time == "06:00":
                        await general_services.send_prayer("ahd")

                    elif current_time == "07:47":
                        await general_services.send_day_info()

                    elif current_time == "09:34":
                        await hadith_services.auto_send()

                    elif current_time == "11:21":
                        await clip_services.auto_send()

                    elif current_time == "13:08":
                        await general_services.send_prayer("tohid")

                    elif current_time == "14:55":
                        await hadith_services.auto_send()

                    elif current_time == "16:42":
                        await book_services.auto_send()

                    elif current_time == "18:29":
                        await general_services.send_prayer("faraj")

                    elif current_time == "20:16":
                        await note_services.auto_send()

                    elif current_time == "22:03":
                        await lecture_services.auto_send()

                    sent_today.add(current_time)
                except Exception as e:
                    await send_to_admins(
                        f"[{current_time}] خطا در اجرای برنامه زمان‌بندی:\n{e}"
                    )

            # ریست کردن لیست زمان‌های اجرا شده در روز بعد
            if current_time == "00:00":
                sent_today.clear()

        await asyncio.sleep(30)
