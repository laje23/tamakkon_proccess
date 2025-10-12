from balethon.objects import InlineKeyboard, InlineKeyboardButton
from models import audio_model


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
    rows = audio_model.get_all_audios()
    keyboards = []
    if rows:
        for row in rows:
            id, file_name, file_id, caption = row
            button = InlineKeyboardButton(str(file_name), f"audio:{id}")
            keyboards.append([button])
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    else:
        keyboards.append(
            [
                InlineKeyboardButton(
                    "جدول خالیست ایجاد مقادیر اولیه", "create_default_audios_row"
                )
            ]
        )
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    return InlineKeyboard(*keyboards)


def note_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("یادداشت جدید", "save_note")],
        [InlineKeyboardButton("ویرایش", "edit_note")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def schaduler_menu(on: bool):
    rows = []
    if on:
        rows.append([InlineKeyboardButton("خاموش کردن زمانبندی", "schaduler_off")])
    else:
        rows.append([InlineKeyboardButton("روشن کردن زمانبندی", "schaduler_on")])
    rows.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    return InlineKeyboard(*rows)


def book_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("کتاب جدید", "save_book")],
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
        [InlineKeyboardButton("ارسال پیام به کانال", "send_to_channel")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def answer_y_n(id):
    return InlineKeyboard(
        [InlineKeyboardButton("بله", f"resend:{id}")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def edit_note_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("ویرایش", "edit_note")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def back_menu():
    return InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_message")])
