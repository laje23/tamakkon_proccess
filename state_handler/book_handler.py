from config import bale_bot, back_menu, user_temp_data
from models.books_model import (
    save_book,
    check_book_exists,
    get_unsent_book,
    edit_book,
)

MESSAGES = {
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

# 🟢 ثبت کتاب جدید


async def input_book_title(message):
    user_id = message.author.id
    user_temp_data[user_id] = {"title": message.text.strip()}
    message.author.set_state("INPUT_BOOK_AUTHOR")
    await bale_bot.send_message(message.chat.id, MESSAGES["enter_author"])


async def input_book_author(message):
    user_id = message.author.id
    user_temp_data[user_id]["author"] = message.text.strip()
    message.author.set_state("INPUT_BOOK_PUBLISHER")
    await bale_bot.send_message(message.chat.id, MESSAGES["enter_publisher"])


async def input_book_publisher(message):
    user_id = message.author.id
    publisher = None if message.text.strip() == "ندارم" else message.text.strip()
    user_temp_data[user_id]["publisher"] = publisher
    message.author.set_state("INPUT_BOOK_EXCERPT")
    await bale_bot.send_message(message.chat.id, MESSAGES["enter_excerpt"])


async def input_book_excerpt(message):
    user_id = message.author.id
    excerpt = None if message.text.strip() == "ندارم" else message.text.strip()
    data = user_temp_data.get(user_id, {})

    try:
        save_book(
            title=data.get("title"),
            author=data.get("author"),
            publisher=data.get("publisher"),
            excerpt=excerpt,
        )
        await bale_bot.send_message(
            message.chat.id, MESSAGES["book_saved"], back_menu()
        )
    except Exception as e:
        await bale_bot.send_message(
            message.chat.id, f"{MESSAGES['book_error']}{str(e)}", back_menu()
        )

    user_temp_data.pop(user_id, None)
    message.author.del_state()


# ✏️ ویرایش کتاب موجود


async def input_book_id_for_edit(message):
    book_id_text = message.text.strip()
    if not book_id_text.isdigit():
        await bale_bot.send_message(
            message.chat.id, MESSAGES["only_number"], back_menu()
        )
        return

    book_id = int(book_id_text)
    if not check_book_exists(book_id):
        await bale_bot.send_message(
            message.chat.id, MESSAGES["book_not_found"], back_menu()
        )
        message.author.del_state()
        return

    book = get_unsent_book()
    if not book or book["id"] != book_id:
        await bale_bot.send_message(
            message.chat.id, MESSAGES["book_already_sent"], back_menu()
        )
        message.author.del_state()
        return

    user_temp_data[message.author.id] = {"edit_book_id": book_id}
    message.author.set_state("EDIT_BOOK_TITLE")
    await bale_bot.send_message(message.chat.id, MESSAGES["enter_new_title"])


async def input_new_title(message):
    user_id = message.author.id
    user_temp_data[user_id]["title"] = message.text.strip()
    message.author.set_state("EDIT_BOOK_AUTHOR")
    await bale_bot.send_message(message.chat.id, MESSAGES["enter_new_author"])


async def input_new_author(message):
    user_id = message.author.id
    user_temp_data[user_id]["author"] = message.text.strip()
    message.author.set_state("EDIT_BOOK_PUBLISHER")
    await bale_bot.send_message(message.chat.id, MESSAGES["enter_new_publisher"])


async def input_new_publisher(message):
    user_id = message.author.id
    publisher = None if message.text.strip() == "ندارم" else message.text.strip()
    user_temp_data[user_id]["publisher"] = publisher
    message.author.set_state("EDIT_BOOK_EXCERPT")
    await bale_bot.send_message(message.chat.id, MESSAGES["enter_new_excerpt"])


async def input_new_excerpt(message):
    user_id = message.author.id
    excerpt = None if message.text.strip() == "ندارم" else message.text.strip()
    data = user_temp_data.get(user_id, {})
    book_id = data.get("edit_book_id")

    try:
        edit_book(
            book_id=book_id,
            title=data.get("title"),
            author=data.get("author"),
            publisher=data.get("publisher"),
            excerpt=excerpt,
        )
        await bale_bot.send_message(
            message.chat.id, MESSAGES["book_edited"], back_menu()
        )
    except Exception as e:
        await bale_bot.send_message(
            message.chat.id, f"{MESSAGES['book_edit_error']}{str(e)}", back_menu()
        )

    user_temp_data.pop(user_id, None)
    message.author.del_state()
