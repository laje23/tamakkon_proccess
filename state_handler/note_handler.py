from config import *
from utils import fa_to_en_int

MESSAGES = {
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


async def first_step_save(message):
    note_number = fa_to_en_int(message.text)
    if note_number <= 0:
        await bale_bot.send_message(
            message.chat.id, MESSAGES["invalid_number"], back_menu()
        )
        return

    if db_notes.check_is_exist(note_number):
        await bale_bot.send_message(
            message.chat.id,
            MESSAGES["note_exists"] + "\n" + MESSAGES["enter_note_text"],
            back_menu(),
        )
        return

    # ایجاد رکورد مادر (با مقادیر اولیه خالی برای محتوا)
    db_notes.save_note(note_number, "", "")

    user_temp_data[message.author.id] = {
        "note_number": note_number,
        "media_type": None,
        "media_file_id": None,
        "part_index": 0,
    }

    message.author.set_state("ASK_MEDIA")
    await bale_bot.send_message(message.chat.id, MESSAGES["ask_media"])


async def handle_media_step(message):
    user_id = message.author.id
    state = message.author.get_state()

    if state != "ASK_MEDIA":
        return

    if message.photo:
        user_temp_data[user_id]["media_type"] = "photo"
        user_temp_data[user_id]["media_file_id"] = message.photo[-1].id
        await bale_bot.send_message(message.chat.id, MESSAGES["media_received"])
        message.author.set_state("INPUT_TEXT_NOTE")

    elif message.video:
        user_temp_data[user_id]["media_type"] = "video"
        user_temp_data[user_id]["media_file_id"] = message.video.id
        await bale_bot.send_message(message.chat.id, MESSAGES["media_received"])
        message.author.set_state("INPUT_TEXT_NOTE")

    elif message.text and message.text.strip().lower() == "ندارم":
        await bale_bot.send_message(message.chat.id, MESSAGES["no_media"])
        message.author.set_state("INPUT_TEXT_NOTE")

    else:
        await bale_bot.send_message(message.chat.id, MESSAGES["invalid_media_response"])


async def handle_text_parts(message):
    user_id = message.author.id
    state = message.author.get_state()

    if state != "INPUT_TEXT_NOTE":
        await bale_bot.send_message(
            message.chat.id, MESSAGES["invalid_number"], back_menu()
        )
        return

    text = message.text.strip()
    note_id = user_temp_data[user_id]["note_number"]

    # گرفتن شماره بخش و ذخیره
    part_index = user_temp_data[user_id]["part_index"]
    db_notes.save_part(note_id, part_index, text)

    # زیاد کردن شمارنده برای دفعه بعد
    user_temp_data[user_id]["part_index"] += 1

    await bale_bot.send_message(message.chat.id, MESSAGES["ask_more_text"])
    message.author.set_state("CONFIRM_MORE_TEXT")


async def confirm_more_text(message):
    user_id = message.author.id
    answer = message.text.strip().lower()

    if answer == "بله":
        message.author.set_state("INPUT_TEXT_NOTE")
        await bale_bot.send_message(message.chat.id, MESSAGES["enter_note_text"])

    elif answer == "خیر":
        # به‌روزرسانی اطلاعات مدیا تو جدول مادر (اگر بود)
        note_id = user_temp_data[user_id]["note_number"]
        file_id = str(user_temp_data[user_id].get("media_file_id", ""))
        media_type = user_temp_data[user_id].get("media_type", "")
        db_notes.edit_media(note_id, file_id, media_type)  # فرضاً این متد رو داری

        await bale_bot.send_message(
            message.chat.id, MESSAGES["note_saved"], back_menu()
        )

        user_temp_data.pop(user_id, None)
        message.author.del_state()

    else:
        await bale_bot.send_message(message.chat.id, MESSAGES["invalid_answer"])
