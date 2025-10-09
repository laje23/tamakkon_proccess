# services/clip_service.py

from services.base_service import BaseService
from utils.respons import success_response, error_response
from utils.decorator import safe_run
from utils.media import file_id_to_bynery
from models import clips_model
import asyncio


class ClipService(BaseService):
    def __init__(self, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال کلیپ‌ها
        """
        super().__init__(db_model=clips_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

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
