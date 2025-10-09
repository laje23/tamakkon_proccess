import asyncio
from datetime import datetime
from pytz import timezone
from utils import get_schaduler_state
from send_message_handler import (
    send_prayer,
    send_day_info,
    auto_send_hadith,
    send_auto_clip,
    send_auto_book,
    auto_send_not,
    send_auto_lecture,  
    send_to_debugger,
)


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
                        await send_prayer("ahd")

                    elif current_time == "07:47":
                        await send_day_info()

                    elif current_time == "09:34":
                        await auto_send_hadith()

                    elif current_time == "11:21":
                        await send_auto_clip()

                    elif current_time == "13:08":
                        await send_prayer("tohid")

                    elif current_time == "14:55":
                        await auto_send_hadith()

                    elif current_time == "16:42":
                        await send_auto_book()

                    elif current_time == "18:29":
                        await send_prayer("faraj")

                    elif current_time == "20:16":
                        await auto_send_not()

                    elif current_time == "22:03":
                        await send_auto_lecture()

                    sent_today.add(current_time)
                except Exception as e:
                    await send_to_debugger(
                        f"[{current_time}] خطا در اجرای برنامه زمان‌بندی:\n{e}"
                    )

            # ریست کردن لیست زمان‌های اجرا شده در روز بعد
            if current_time == "00:00":
                sent_today.clear()

        await asyncio.sleep(30)
