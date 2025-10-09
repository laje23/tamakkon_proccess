# services/book_service.py

from services.base_service import BaseService
from utils.respons import success_response, error_response
from utils.decorator import safe_run
from models import books_model 
from utils.keyboard import back_menu


class BookService(BaseService):
    def __init__(self , user_temp_data , bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال کتاب‌ها
        """
        super().__init__(db_model=books_model, bale_bot=bale_bot, eitaa_bot=eitaa_bot)
        self.MESSAGES = {
            "enter_title": "عنوان کتاب رو وارد کن:",
            "enter_author": "نام نویسنده کتاب رو وارد کن:",
            "enter_publisher": "نام ناشر رو وارد کن (یا بنویس «ندارم»):",
            "enter_excerpt": "گزیده‌ای از کتاب رو وارد کن (یا بنویس «ندارم»):",
            "book_saved": "✅ کتاب با موفقیت ذخیره شد.",
            "book_error": "❌ خطا در ذخیره کتاب: ",
            "enter_book_id": "شناسه کتابی که می‌خوای ویرایش کنی رو وارد کن:",
            "book_not_found": "❌ کتابی با این شناسه پیدا نشد.",
            "book_already_sent": "این کتاب قبلاً ارسال شده و قابل ویرایش نیست.",
            "enter_new_title": "عنوان جدید کتاب رو وارد کن:",
            "enter_new_author": "نام نویسنده جدید رو وارد کن:",
            "enter_new_publisher": "نام ناشر جدید رو وارد کن (یا بنویس «ندارم»):",
            "enter_new_excerpt": "گزیده جدید رو وارد کن (یا بنویس «ندارم»):",
            "book_edited": "✅ کتاب با موفقیت ویرایش شد.",
            "book_edit_error": "❌ خطا در ویرایش کتاب: ",
            "only_number": "لطفاً فقط عدد وارد کن.",
        }
        self.user_temp_data = user_temp_data
        
        
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


    @safe_run
    async def input_book_title(self ,message):
        user_id = message.author.id
        self.user_temp_data[user_id] = {"title": message.text.strip()}
        message.author.set_state("INPUT_BOOK_AUTHOR")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_author"])

    @safe_run
    async def input_book_author(self,message):
        user_id = message.author.id
        self.user_temp_data[user_id]["author"] = message.text.strip()
        message.author.set_state("INPUT_BOOK_PUBLISHER")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_publisher"])
        
    @safe_run
    async def input_book_publisher(self,message):
        user_id = message.author.id
        publisher = None if message.text.strip() == "ندارم" else message.text.strip()
        self.user_temp_data[user_id]["publisher"] = publisher
        message.author.set_state("INPUT_BOOK_EXCERPT")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_excerpt"])
        
    @safe_run
    async def input_book_excerpt(self,message):
        user_id = message.author.id
        excerpt = None if message.text.strip() == "ندارم" else message.text.strip()
        data = self.user_temp_data.get(user_id, {})

        try:
            self.db.save_book(
                title=data.get("title"),
                author=data.get("author"),
                publisher=data.get("publisher"),
                excerpt=excerpt,
            )
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["book_saved"], back_menu()
            )
        except Exception as e:
            await self.bale_bot.send_message(
                message.chat.id, f"{self.MESSAGES['book_error']}{str(e)}", back_menu()
            )

        self.user_temp_data.pop(user_id, None)
        message.author.del_state()

    @safe_run
    async def input_book_id_for_edit(self, message):
        book_id_text = message.text.strip()
        if not book_id_text.isdigit():
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["only_number"], back_menu()
            )
            return

        book_id = int(book_id_text)
        if not self.db.check_book_exists(book_id):
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["book_not_found"], back_menu()
            )
            message.author.del_state()
            return

        book = self.db.get_unsent_book()
        if not book or book["id"] != book_id:
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["book_already_sent"], back_menu()
            )
            message.author.del_state()
            return

        self.user_temp_data[message.author.id] = {"edit_book_id": book_id}
        message.author.set_state("EDIT_BOOK_TITLE")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_new_title"])

    @safe_run
    async def input_new_title(self,message):
        user_id = message.author.id
        self.user_temp_data[user_id]["title"] = message.text.strip()
        message.author.set_state("EDIT_BOOK_AUTHOR")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_new_author"])

    @safe_run
    async def input_new_author(self ,message):
        user_id = message.author.id
        self.user_temp_data[user_id]["author"] = message.text.strip()
        message.author.set_state("EDIT_BOOK_PUBLISHER")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_new_publisher"])

    @safe_run
    async def input_new_publisher(self,message):
        user_id = message.author.id
        publisher = None if message.text.strip() == "ندارم" else message.text.strip()
        self.user_temp_data[user_id]["publisher"] = publisher
        message.author.set_state("EDIT_BOOK_EXCERPT")
        await self.bale_bot.send_message(message.chat.id, self.MESSAGES["enter_new_excerpt"])

    @safe_run
    async def input_new_excerpt(self,message):
        user_id = message.author.id
        excerpt = None if message.text.strip() == "ندارم" else message.text.strip()
        data = self.user_temp_data.get(user_id, {})
        book_id = data.get("edit_book_id")

        try:
            self.db.edit_book(
                book_id=book_id,
                title=data.get("title"),
                author=data.get("author"),
                publisher=data.get("publisher"),
                excerpt=excerpt,
            )
            await self.bale_bot.send_message(
                message.chat.id, self.MESSAGES["book_edited"], back_menu()
            )
        except Exception as e:
            await self.bale_bot.send_message(
                message.chat.id, f"{self.MESSAGES['book_edit_error']}{str(e)}", back_menu()
            )

        self.user_temp_data.pop(user_id, None)
        message.author.del_state()
