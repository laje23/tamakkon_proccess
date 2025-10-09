from balethon.objects import InlineKeyboard, InlineKeyboardButton
from balethon import Client
from app_manager import EitaaBot
from models import hadith as db_hadith
from models import notes as db_notes
from models import clips as db_clips
from models import books as db_books
from models import audio as db_audios
from models import lecture as db_lecture
import asyncio
import threading
import os


user_temp_data = {}
schaduler_state = False
# assignment initial variables...................................


bale_bot = Client(os.getenv("BALE_BOT_TOKEN"), time_out=60.0)
eitaa_bot = EitaaBot(os.getenv("EITAA_BOT_TOKEN"))

debugger_id = os.getenv("DEBUGER_ID")

group_reserch_hadith_id = int(os.getenv("RESERCH_HADITH"))
group_reserch_clip_id = int(os.getenv("RESERCH_CLIP_ID"))
group_reserch_lecture_id = int(os.getenv("RESERCH_LECTURE_ID"))


bale_channel_id = int(os.getenv("CHANNEL_BALE"))
eitaa_channel_id = int(os.getenv("CHANNEL_EITAA"))
eitaa_channel_id_test = int(os.getenv("CHANNEL_EITAA_TEST"))


base_image_url = os.getenv("BASE_IMAGE_URL")
base_mentioning_image_url = os.getenv("BASE_DAY_URL")


hadith_photo_url = base_image_url + "hadith.jpg"


admins = [
    int(admin_id)
    for admin_id in os.getenv("ADMINS_ID", "").split(",")
    if admin_id.strip()
]


# process messages  ........................................................
# 🧠 پردازش پیام‌ها
def process_hadith_message(text: str, id: int | str, eitaa=False) -> str:
    if eitaa:
        return f"""📗 حدیث روز 
{text}\n
#حدیث
#{id}
@tamakkon_ir"""

    else:
        return f"""📗 حدیث روز
{text}\n
#حدیث
#{id}
@tamakkon_ir"""


def process_note_message(text: str, id: int | str) -> str:
    emoji_map = {
        i: num
        for i, num in enumerate(["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"])
    }
    emojied = "".join(emoji_map[int(c)] for c in str(id)[::-1])
    return f"""#یادداشت_استاد
شماره {emojied}

{text}

صفحه رسمی استاد در فارس من:
https://farsnews.ir/shnavvab

#نهضت_تمکن
@tamakkon_ir"""


# keyboard buttens ......................................
# 🧩 کیبوردها


def main_menu(is_admin: bool):
    rows = [[InlineKeyboardButton("در حال بروزرسانی", "in_update")]]

    if is_admin:
        rows.append([InlineKeyboardButton("مدیریت پیام‌ها", "back_to_message")])

    return InlineKeyboard(*rows)


def message_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("ارسال ها", "send_menu")],
        [InlineKeyboardButton("ذخیره و ویرایش", "add_and_edit")],
        [InlineKeyboardButton("صوت های ارسالی", "change_audio_file_id")],
        [InlineKeyboardButton("گرفتن آمار", "get_status")],
        [InlineKeyboardButton("زمانبندی", "schaduler_menu")],
        [InlineKeyboardButton("بازگشت", "back_to_main")],
    )


def audios_menu():
    rows = db_audios.get_all_audios()
    keyboards = []
    if rows:

        for row in rows:
            id, file_name, file_id, caption = row
            button = InlineKeyboardButton(str(file_name), f"audio:{id}")
            keyboards.append([button])
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    else:
        button = InlineKeyboardButton(
            "جدول خالیست ایجاد مقادیر اولیه ", "create_default_audios_row"
        )
        keyboards.append([button])
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    return InlineKeyboard(*keyboards)


def note_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("یادداشت جدید ", "save_note")],
        [InlineKeyboardButton("ویرایش", "edit_note")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def schaduler_menu(on):
    rows = []
    if on:
        rows.append([InlineKeyboardButton("خاموش کردن زمانبندی", "schaduler_off")])
    else:
        rows.append([InlineKeyboardButton("روشن کردن زمانبندی", "schaduler_on")])

    rows.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    return InlineKeyboard(*rows)


def book_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("کتاب جدید ", "save_book")],
        [InlineKeyboardButton("ویرایش", "edit_book")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def save_or_edit_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("یادداشت", "note_menu")],
        [InlineKeyboardButton("کتاب", "book_menu")],
        [InlineKeyboardButton("کلیپ", "clip_menu")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def send_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("حدیث", "auto_send_hadith")],
        [InlineKeyboardButton("یادداشت", "auto_send_note")],
        [InlineKeyboardButton("کتاب", "auto_send_book")],
        [InlineKeyboardButton("کلیپ", "auto_send_clip")],
        [InlineKeyboardButton("سخنرانی", "auto_send_lecture")],
        [InlineKeyboardButton("ارسال پیام به کانال ", "send_to_channel")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def answer_y_n(id):
    return InlineKeyboard(
        [InlineKeyboardButton(f"بله", f"resend:{id}")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def edit_note_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("ویرایش", "edit_note")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def back_menu():
    return InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_message")])
