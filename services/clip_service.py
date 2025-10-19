# services/clip_service.py

from services.base_service import BaseService
from utils.response import success_response, error_response
from utils.decorator import safe_run
from utils.media import file_id_to_bynery
from utils.keyboard import back_menu
from models import clips_model
import asyncio


class ClipService(BaseService):
    def __init__(self, user_temp_data, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال کلیپ‌ها
        """
        super().__init__(db_model=clips_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
        self.user_temp_data = user_temp_data
        self.MESSAGES = {
            "invalid_number": "❗️ لطفاً فقط عدد مثبت وارد کنید.",
            "only_number": "لطفاً فقط عدد وارد کن.",
            "clip_not_found": "❌ کلیپی با این شناسه پیدا نشد.",
            "clip_already_sent": "❌ این کلیپ قبلاً ارسال شده و قابل ویرایش نیست.",
            "enter_id": "شماره کلیپ را وارد کنید:",
            "send_clip": "لطفا کلیپ را ارسال کنید.",
            "send_caption": "کپشن کلیپ را ارسال کن:",
            "clip_caption_saved": "✅ کلیپ و کپشن با موفقیت ذخیره شدند.",
            "enter_new_caption": "کپشن جدید را ارسال کنید:",
            "caption_edited": "✅ کپشن کلیپ با موفقیت ویرایش شد.",
            "error_editing_caption": "❌ خطا در ویرایش کپشن:",
        }

    @safe_run
    async def auto_send(self):
        """
        ارسال خودکار یک کلیپ به کانال‌های بله و ایتا
        """
        clip = self.db.auto_return_file_id()
        if not clip:
            raise Exception("هیچ کلیپی آماده ارسال نیست")

        id, file_id, caption = clip

        # گرفتن باینری فایل از بات
        bin_file = await file_id_to_bynery(file_id, self.bale_bot)

        # اضافه کردن کپشن اختصاصی
        caption = (caption or "") + "\n\n#کلیپ\n@tamakkon_ir"

        # ارسال هم‌زمان با متد پایه
        await self.send_media("video", bin_file, caption)

        # آپدیت وضعیت
        self.db.mark_clip_sent(id)

        return success_response(f"کلیپ با شناسه {id} ارسال شد")

    @safe_run
    async def handle_new_clip(self, message):
        user_id = message.author.id
        self.user_temp_data[user_id] = {}

        if message.video:
            clip_file_id = message.video.id
        else:
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["send_clip"]
            )
            return

        self.user_temp_data[user_id]["clip_file_id"] = clip_file_id
        message.author.set_state("INPUT_CLIP_CAPTION")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["send_caption"])

    @safe_run
    async def handle_clip_caption(self, message):
        user_id = message.author.id
        file_id = self.user_temp_data[user_id].get("clip_file_id")
        caption = message.text.strip()

        self.db.save_clip(file_id, caption)
        await self.bale_bot.send_message(
            message.chat.id, self.MESSAGES["clip_caption_saved"], back_menu()
        )

        self.user_temp_data.pop(user_id, None)
        message.author.del_state()

    @safe_run
    async def handle_edit_caption(self, message):
        user_id = message.author.id
        id = self.user_temp_data[user_id].get("edit_id")
        new_caption = message.text.strip()

        self.db.edit_clip_caption(id, new_caption)
        await self.bale_bot.send_message(
            message.chat.id, self.MESSAGES["caption_edited"], back_menu()
        )

        self.user_temp_data.pop(user_id, None)
        message.author.del_state()
