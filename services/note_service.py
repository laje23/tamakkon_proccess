from services.base_service import BaseService
from utils.decorator import safe_run
from utils.respons import success_response
from utils.message_prosseccing import process_note_message
from models import (
    notes_model,
)  # فرض می‌کنیم notes_model شامل توابع و کلاس‌های NoteTableManager و TextPartManager باشد
from utils.text_utils import prepare_processed_messages, fa_to_en_int
from utils.media import file_id_to_bynery
from utils.keyboard import back_menu


class NoteService(BaseService):
    def __init__(self, user_temp_data, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال یادداشت‌ها
        """
        super().__init__(db_model=notes_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
        self.MESSAGES = {
            "invalid_number": "❗️ لطفاً فقط عدد مثبت وارد کنید.",
            "note_exists": "این یادداشت موجود است. می‌خواهید آن را ویرایش کنید؟",
            "enter_note_text": "متن یادداشت رو بفرستید",
            "note_saved": "یادداشت با موفقیت ذخیره شد.",
            "note_not_found": "شماره یادداشت پیدا نشد! دوباره امتحان کن.",
            "note_does_not_exist": "این یادداشت موجود نیست. ابتدا آن را ایجاد کنید.",
            "note_sent": "یادداشت ارسال شده است و قابل ویرایش نیست.",
            "note_edited": "یادداشت ویرایش شد.",
            "ask_more_text": "متن بیشتری داری؟ لطفا پاسخ بده: بله / خیر",
            "invalid_answer": "لطفا فقط 'بله' یا 'خیر' جواب بده.",
            "ask_media": "آیا می‌خواهی همراه یادداشت عکس یا فیلمی ارسال کنی؟ اگر داری ارسال کن، اگر نه بنویس 'ندارم'.",
            "media_received": "فایل دریافت شد. حالا لطفاً متن یادداشت رو بفرست.",
            "no_media": "باشه، بدون فایل. حالا لطفاً متن یادداشت رو بفرست.",
            "invalid_media_response": "لطفاً فایل بفرست یا بنویس 'ندارم'.",
        }
        self.user_temp_data = user_temp_data

    @safe_run
    async def auto_send(self):
        """
        ارسال خودکار یک یادداشت به کانال‌ها
        """
        # گرفتن یادداشت آماده ارسال
        note = self.db.get_unsent_note()
        if not note:
            raise Exception("هیچ یادداشتی برای ارسال موجود نیست")

        text_id, file_id, media_type = note

        # گرفتن بخش‌های متن
        parts = self.db.get_parts(text_id)
        if not parts:
            raise Exception("هیچ بخشی از متن موجود نیست")

        # آماده‌سازی پیام‌ها
        messages = prepare_processed_messages(
            parts, text_id, process_func=process_note_message
        )

        # اگر یادداشت شامل فایل باشد
        if file_id and media_type:
            file = await file_id_to_bynery(file_id, self.bale_bot)

            if media_type == "photo":
                await self.bale_bot.send_photo(
                    self.bale_channel_id, file, messages[0]
                )
            elif media_type == "video":
                await self.bale_bot.send_video(
                    self.bale_channel_id, file.read(), messages[0]
                )
            elif media_type == "audio":
                await self.bale_bot.send_audio(
                    self.bale_channel_id, file.read(), messages[0]
                )

            await self.eitaa_bot.send_file(self.eitaa_channel_id, file, messages[0])
            messages.pop(0)
    @safe_run
    async def auto_send(self):
        """
        ارسال خودکار یک یادداشت به کانال‌ها
        """
        # گرفتن یادداشت آماده ارسال
        note = self.db.get_unsent_note()
        if not note:
            raise Exception("هیچ یادداشتی برای ارسال موجود نیست")

        text_id, file_id, media_type = note

        # گرفتن بخش‌های متن
        parts = self.db.get_parts(text_id)
        if not parts:
            raise Exception("هیچ بخشی از متن موجود نیست")

        # آماده‌سازی پیام‌ها
        messages = prepare_processed_messages(
            parts, text_id, process_func=process_note_message
        )

        # اگر یادداشت شامل فایل باشد
        if file_id and media_type:
            file = await file_id_to_bynery(file_id, self.bale_bot)

            if media_type == "photo":
                await self.bale_bot.send_photo(
                    self.bale_channel_id, file, messages[0]
                )
            elif media_type == "video":
                await self.bale_bot.send_video(
                    self.bale_channel_id, file.read(), messages[0]
                )
            elif media_type == "audio":
                await self.bale_bot.send_audio(
                    self.bale_channel_id, file.read(), messages[0]
                )

            await self.eitaa_bot.send_file(self.eitaa_channel_id, file, messages[0])
            messages.pop(0)

        # ارسال بخش‌های متنی باقی‌مانده
        for msg in messages:
            await self.bale_bot.send_message(self.bale_channel_id, msg)
            await self.eitaa_bot.send_message(self.eitaa_channel_id, msg)

        # علامت‌گذاری یادداشت به عنوان ارسال شده
        self.db.mark_sent(text_id)
        return success_response("یادداشت ارسال شد")

    @safe_run
    async def first_step_save(self, message):
        note_number = fa_to_en_int(message.text)
        if note_number <= 0:
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["invalid_number"], back_menu()
            )
            return

        if self.db.check_is_exist(note_number):
            await self.bale_bot.send_message(
                message.chat.id,
                self.MESSAGES["note_exists"] + "\n" + self.MESSAGES["enter_note_text"],
                back_menu(),
            )
            return
        self.db.save_note(note_number, "", "")

        self.user_temp_data[message.author.id] = {
            "note_number": note_number,
            "media_type": None,
            "media_file_id": None,
            "part_index": 0,
        }

        message.author.set_state("ASK_MEDIA")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["ask_media"])

    @safe_run
    async def handle_media_step(self, message):
        user_id = message.author.id
        state = message.author.get_state()

        if state != "ASK_MEDIA":
            return

        if message.photo:
            self.user_temp_data[user_id]["media_type"] = "photo"
            self.user_temp_data[user_id]["media_file_id"] = message.photo[-1].id
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["media_received"]
            )
            message.author.set_state("INPUT_TEXT_NOTE")

        elif message.video:
            self.user_temp_data[user_id]["media_type"] = "video"
            self.user_temp_data[user_id]["media_file_id"] = message.video.id
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["media_received"]
            )
            message.author.set_state("INPUT_TEXT_NOTE")

        elif message.text and message.text.strip().lower() == "ندارم":
            await self.bale_bot.send_message(message.chat.id, self.MESSAGES["no_media"])
            message.author.set_state("INPUT_TEXT_NOTE")

        else:
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["invalid_media_response"]
            )

    @safe_run
    async def handle_text_parts(self, message):
        user_id = message.author.id
        state = message.author.get_state()

        if state != "INPUT_TEXT_NOTE":
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["invalid_number"], back_menu()
            )
            return

        text = message.text.strip()
        note_id = self.user_temp_data[user_id]["note_number"]

        # گرفتن شماره بخش و ذخیره
        part_index = self.user_temp_data[user_id]["part_index"]
        self.db.save_part(note_id, part_index, text)

        # زیاد کردن شمارنده برای دفعه بعد
        self.user_temp_data[user_id]["part_index"] += 1

        await self.bale_bot.send_message(
            message.chat.id, self.MESSAGES["ask_more_text"]
        )
        message.author.set_state("CONFIRM_MORE_TEXT")

    @safe_run
    async def confirm_more_text(self, message):
        user_id = message.author.id
        answer = message.text.strip().lower()

        if answer == "بله":
            message.author.set_state("INPUT_TEXT_NOTE")
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["enter_note_text"]
            )

        elif answer == "خیر":
            # به‌روزرسانی اطلاعات مدیا تو جدول مادر (اگر بود)
            note_id = self.user_temp_data[user_id]["note_number"]
            file_id = str(self.user_temp_data[user_id].get("media_file_id", ""))
            media_type = self.user_temp_data[user_id].get("media_type", "")
            self.db.edit_media(note_id, file_id, media_type)  # فرضاً این متد رو داری

            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["note_saved"], back_menu()
            )

            self.user_temp_data.pop(user_id, None)
            message.author.del_state()

        else:
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["invalid_answer"]
            )
