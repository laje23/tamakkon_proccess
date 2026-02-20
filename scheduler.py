import asyncio
from datetime import datetime
from utils.scheduler_utils import get_scheduler_state
from utils.notifiter import send_to_admins
from pytz import timezone
from config.service_configs import *


async def scheduled_messages():
    sent_today = set()

    auto_send_counter = 0
    retry_failed_counter = 0

    while True:
        iran = timezone("Asia/Tehran")
        now = datetime.now(iran)
        current_time = now.strftime("%H:%M")

        if get_scheduler_state():
            if current_time not in sent_today:
                try:
                    if current_time == "06:00":
                        await general_services.send_prayer("ahd")

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

            if current_time == "00:00":
                sent_today.clear()

            # ---------- شمارنده‌ها ----------
            auto_send_counter += 1
            retry_failed_counter += 1

            # مثلا هر 10 بار → auto_send
            if auto_send_counter >= 10:
                try:
                    await schedul_message_service.auto_send()
                except Exception as e:
                    await send_to_admins(f"[CRON] خطا در auto_send:\n{e}")
                finally:
                    auto_send_counter = 0  # ریست

            # مثلا هر 20 بار → retry_failed
            if retry_failed_counter >= 20:
                try:
                    await schedul_message_service.retry_failed()
                except Exception as e:
                    await send_to_admins(f"[CRON] خطا در retry_failed:\n{e}")
                finally:
                    retry_failed_counter = 0  # ریست

        await asyncio.sleep(30)
