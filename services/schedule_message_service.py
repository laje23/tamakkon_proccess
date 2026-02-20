# services/scheduled_message_state_service.py
import asyncio

from services.base_service import BaseService
from utils.response import success_response, error_response
from utils.keyboard import (
    back_to_message_menu,
    week_days_menu,
    day_hours_menu,
    hour_minutes_menu,
    schedule_message_view_menu,
)
from models import schedule_message_model
from models.media_model import MediaTableManager
from utils.media import file_id_to_bynery
from utils.datetime import combine_date_and_time_auto , gregorian_to_jalali
from utils.media import file_id_to_bynery


class ScheduledMessageService(BaseService):
    """
    سرویس مدیریت پیام‌های زمانبندی شده با state کاربر
    """

    def __init__(self, user_temp_data, bale_bot, eitaa_bot):
        super().__init__(
            db_model=schedule_message_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot
        )
        self.user_temp_data = user_temp_data
        self.MESSAGES = {
            "enter_text": "📩 لطفاً متن پیام خود را وارد کنید:",
            "enter_media": "🎬 لطفاً فایل مدیا را ارسال کنید (اختیاری):",
            "enter_time": "⏰ زمان ارسال پیام را به فرمت YYYY-MM-DD HH:MM وارد کنید:",
            "message_saved": "✅ پیام زمانبندی شده با موفقیت ذخیره شد.",
            "no_pending": "❌ هیچ پیام زمانبندی شده آماده ارسال نیست.",
            "invalid_time": "❌ فرمت زمان اشتباه است. لطفاً به شکل YYYY-MM-DD HH:MM وارد کنید.",
        }

    # ---------- مراحل گرفتن پیام از کاربر ----------
    async def start_message_flow(self, author):
        self.user_temp_data[author.id] = {}
        author.set_state("INPUT_MEDIA")
        await self.bale_bot.send_message(
            author.id, self.MESSAGES["enter_media"], back_to_message_menu()
        )

    async def handle_media(self, message):
        user_id = message.author.id
        if message.video:
            media_id = message.video.id
            media_type = "video"
        elif message.audio:
            media_id = message.audio.id
            media_type = "audio"
        elif message.document:
            media_id = message.document.id
            media_type = "audio"
        elif message.photo:
            media_id = message.photo[-1].id  # آخرین سایز عکس
            media_type = "photo"
        else:
            media_id = None  # اگر کاربر چیزی نفرستاد، مدیا اختیاریه

        if media_id:
            self.user_temp_data[user_id]["media_id"] = media_id
            self.user_temp_data[user_id]["media_type"] = media_type
        message.author.set_state("INPUT_TEXT")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_text"])

    async def handle_days_send_time(self, message):
        user_id = message.author.id
        text = message.text.strip()
        self.user_temp_data[user_id]["content"] = text
        await self.bale_bot.send_message(
            message.chat.id, "میخواهید در کدام روز ارسال شود", week_days_menu()
        )

    async def handel_hour_send_time(self, user_id, message_id, day_date):
        await self.bale_bot.edit_message_text(
            user_id,
            message_id,
            "یک ساعت برای ارسال انتخاب کنید",
            day_hours_menu(day_date=day_date),
        )

    async def handel_minute_send_time(self, user_id, message_id, day_date, hour):
        await self.bale_bot.edit_message_text(
            user_id,
            message_id,
            "یک دقیقه برای ارسال انتخاب کنید",
            hour_minutes_menu(day_date=day_date, hour=hour),
        )

    async def save_scheduled_message(self, user_id, message_id, day_date, hour, minute):
        datetime = combine_date_and_time_auto(
            date_str=day_date, time_str=f"{hour}:{minute}:00"
        )

        user_data = self.user_temp_data.get(user_id, {})

        media_id = user_data.get("media_id")
        content = user_data.get("content")
        media_type = user_data.get("media_type")

        self.db.insert_message(
            send_at=datetime,
            content=content,
            media_file_id=media_id,
            media_type=media_type,
        )

        await self.bale_bot.edit_message_text(
            user_id, message_id, "زمانبندی ذخیره شد", back_to_message_menu()
        )

    # ---------- ارسال خودکار پیام‌های آماده ----------
    async def auto_send(self, limit=5):
        pending_messages = self.db.select_pending(limit=limit)
        if not pending_messages:
            return error_response(self.MESSAGES["no_pending"])

        for msg in pending_messages:
            msg_id, media_id, content, send_at, file_id, media_type = msg

            try:
                # پیام مدیا
                if file_id:
                    bin_file = await file_id_to_bynery(file_id, self.bale_bot)
                    await self.send_media(media_type, bin_file, caption=content)

                # پیام متنی
                elif content:
                    await self.send_text(content)

                self.db.update_status(msg_id, "sent")

            except Exception as e:
                self.db.increment_retry(msg_id)
                self.db.update_status(msg_id, "failed")

        return success_response(f"{len(pending_messages)} پیام بررسی و ارسال شد.")

    async def retry_failed(self, limit=5, max_retry=3):
        failed_messages = self.db.get_retry_faild_messages(
            limit=limit, max_retry=max_retry
        )
        if not failed_messages:
            return

        for msg in failed_messages:
            msg_id, media_id, content, send_at, file_id, media_type, retry_count = msg

            try:
                if file_id:
                    bin_file = await file_id_to_bynery(file_id, self.bale_bot)
                    await self.send_media(media_type, bin_file, caption=content)

                elif content:
                    await self.send_text(content)

                self.db.update_status(msg_id, "sent")

            except Exception:
                self.db.increment_retry(msg_id)

    async def send_schedule_message_by_id(
        self, schedule_message_id, chat_id, message_id
    ):
        message_info = self.db.get_message_by_id(schedule_message_id)

        if message_info:
            id, media_id, content, send_at, status, retry_count = message_info
            date= str(send_at).split("+")[0]
            date =gregorian_to_jalali(date)
            if media_id:
                with MediaTableManager() as db:
                    media_info = db.get_media_by_id(media_id)
                    if media_info:
                        _, filename, file_id, caption, type, sent = media_info
                        bin_file = await file_id_to_bynery(file_id, self.bale_bot)
                        if type == "audio":
                            message = await self.bale_bot.send_audio(
                                chat_id,
                                bin_file.read(),
                                caption=str(
                                    content
                                    + f"\nتاریخ ارسال : {date} \n وضعیت ارسال :{status} -> تعداد ارسال {retry_count}"
                                ),
                            )
                        if type == "video":
                            message = await self.bale_bot.send_video(
                                chat_id,
                                bin_file.read(),
                                caption=str(
                                    content
                                    + f"\nتاریخ ارسال : {date} \n وضعیت ارسال :{status} -> تعداد ارسال {retry_count}"
                                ),
                            )
                        if type == "photo":
                            message = await self.bale_bot.send_photo(
                                chat_id,
                                bin_file.read(),
                                caption=str(
                                    content
                                    + f"\nتاریخ ارسال : {date} \n وضعیت ارسال :{status} -> تعداد ارسال {retry_count}"
                                ),
                            )
                        await self.bale_bot.edit_message_text(
                            chat_id,
                            message_id,
                            "انتخاب کنید",
                            schedule_message_view_menu(
                                message_db_id=schedule_message_id,
                                sent_message_id=f'{message.id}:{message.chat.id}'
                            ),
                        )
            else:
                message = await self.bale_bot.send_message(chat_id,content+ f"\nتاریخ ارسال : {date} \n وضعیت ارسال :{status} -> تعداد ارسال {retry_count}")
                await self.bale_bot.edit_message_text(
                    chat_id,
                    message_id,
                    "انتخاب کنید",
                    schedule_message_view_menu(message_db_id=schedule_message_id  , sent_message_id=f'{message.id}:{message.chat.id}'),
                )
