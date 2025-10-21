# services/hadith_service.py

from .base_service import BaseService
from utils.response import success_response, error_response
from utils.message_prosseccing import process_hadith_message
from models import hadith_model as db_hadith


class HadithService(BaseService):
    def __init__(self, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال حدیث‌ها
        """
        super().__init__(db_model=db_hadith, bale_bot=bale_bot, eitaa_bot=eitaa_bot)

    async def auto_send(self):
        """
        ارسال خودکار حدیث به کانال‌های بله و ایتا
        """
        result = self.db.return_auto_content()
        if not result:
            return error_response("هیچ حدیثی برای ارسال موجود نیست")

        content, id = result

        # قالب‌بندی پیام برای هر پلتفرم
        text_bale = process_hadith_message(content, id, eitaa=False)
        text_eitaa = process_hadith_message(content, id, eitaa=True)

        # ارسال هم‌زمان به بله و ایتا
        await self.send_text(text_bale, text_eitaa)

        # به‌روزرسانی وضعیت حدیث
        self.db.mark_sent(id)

        return success_response(f"حدیث با شناسه {id} ارسال شد")
