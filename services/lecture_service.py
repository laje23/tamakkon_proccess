# services/lecture_service.py

from services.base_service import BaseService
from utils.respons import success_response
from utils.decorator import safe_run
from utils.media import file_id_to_bynery
from models import lecture_model



class LectureService(BaseService):
    def __init__(self, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال سخنرانی‌ها
        """
        super().__init__(db_model=lecture_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    @safe_run
    async def auto_send(self):
        """
        ارسال خودکار یک سخنرانی به کانال‌های بله و ایتا
        """
        lecture = self.db.auto_return_lecture()
        if not lecture:
            raise Exception("هیچ سخنرانی آماده ارسال نیست")

        id, file_id, caption = lecture

        # گرفتن باینری فایل از بات
        bin_file = await file_id_to_bynery(file_id, self.bale_bot)

        # اضافه کردن کپشن اختصاصی
        caption = (caption or "") + "\n\n#سخنرانی\n@tamakkon_ir"

        # ارسال هم‌زمان با متد پایه
        await self.send_media("audio", bin_file, caption)

        # آپدیت وضعیت
        self.db.mark_lecture_sent(id)

        return success_response(f"سخنرانی با شناسه {id} ارسال شد")
