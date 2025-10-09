# services/book_service.py

from services.base_service import BaseService
from utils.respons import success_response, error_response
from utils.decorator import safe_run
from models import books_model 


class BookService(BaseService):
    def __init__(self, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال کتاب‌ها
        """
        super().__init__(db_model=books_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
        
    @safe_run
    async def auto_send(self):
        """
        ارسال خودکار یک کتاب به کانال‌های بله و ایتا
        """
        book = self.db.get_unsent_book()
        if not book:
            raise Exception("کتاب جدیدی برای ارسال موجود نیست")

        # قالب‌بندی پیام
        text = (
            f"📖 معرفی کتاب روز\n\n"
            f"عنوان: {book['title']}\n"
            f"نویسنده: {book['author']}\n"
            f"ناشر: {book['publisher'] or 'ناشر نامشخص'}\n\n"
            f"معرفی کتاب:\n{book['excerpt'] or '...'}\n\n"
            "🌹 اللهم عجل لولیک الفرج 🌹\n\n"
            "#معرفی_کتاب\n@tamakkon_ir"
        )

        # ارسال هم‌زمان به بله و ایتا از متد پایه
        await self.send_text(text, text)

        # به‌روزرسانی وضعیت کتاب
        self.db.mark_book_sent(book["id"])

        return success_response(f"کتاب '{book['title']}' ارسال شد")
