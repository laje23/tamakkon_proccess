from services.base_service import BaseService
from utils.decorator import safe_run
from utils.respons import success_response, error_response
from models import notes_model  # فرض می‌کنیم notes_model شامل توابع و کلاس‌های NoteTableManager و TextPartManager باشد
from utils.text_utils import prepare_processed_messages
from utils.media import  file_id_to_bynery 

class NoteService(BaseService):
    def __init__(self, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال یادداشت‌ها
        """
        super().__init__(db_model=notes_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

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
        messages = prepare_processed_messages(parts, text_id)

        # اگر یادداشت شامل فایل باشد
        if file_id and media_type:
            file = await file_id_to_bynery(file_id, self.bale_bot)

            if media_type == "photo":
                await self.bale_bot.send_photo(self.bale_channel_id, file.read(), messages[0])
            elif media_type == "video":
                await self.bale_bot.send_video(self.bale_channel_id, file.read(), messages[0])
            elif media_type == "audio":
                await self.bale_bot.send_audio(self.bale_channel_id, file.read(), messages[0])

            await self.eitaa_bot.send_file(self.eitaa_channel_id, file, messages[0])
            messages.pop(0)

        # ارسال بخش‌های متنی باقی‌مانده
        for msg in messages:
            await self.bale_bot.send_message(self.bale_channel_id, msg)
            await self.eitaa_bot.send_message(self.eitaa_channel_id, msg)

        # علامت‌گذاری یادداشت به عنوان ارسال شده
        self.db.mark_sent(text_id)
        return success_response("یادداشت ارسال شد")

