from balethon.objects import InlineKeyboard, InlineKeyboardButton
from models import audios_model, qaa_collection_model, qaa_questions_model, user_model


def main_menu(user_id):
    person = user_model.get_user(user_id)
    if not person:
        rows = [[InlineKeyboardButton("ورود", "login")]]
    else:
        id, user_id, name, phone_number, is_admin = person
        rows = [[InlineKeyboardButton("مسابقات", "qaa_collection_to_user")]]
        if is_admin == 1:
            rows.append([InlineKeyboardButton("مدیریت پیام‌ها", "back_to_message")])

    return InlineKeyboard(*rows)


def message_menu():
    return InlineKeyboard(
        [InlineKeyboardButton("ارسال ها", "send_menu")],
        [InlineKeyboardButton("مسابقات", "qaa_menu")],
        [InlineKeyboardButton("ذخیره و ویرایش", "add_and_edit")],
        [InlineKeyboardButton("صوت های ارسالی", "change_audio_file_id")],
        [InlineKeyboardButton("گرفتن آمار", "get_status")],
        [InlineKeyboardButton("زمانبندی", "schaduler_menu")],
        [InlineKeyboardButton("بازگشت", "back_to_main")],
    )


def qaa_to_users_menu():
    collections = qaa_collection_model.get_pos_collections(active=True)
    keyboards = []
    if collections:
        for id, title, description in collections:
            button = InlineKeyboardButton(
                title, f"qaa_doing_user:{id}"
            )
            keyboards.append([button])
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_main")])
    else:
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_main")])

    return InlineKeyboard(*keyboards)


def qaa_menu():
    collections = qaa_collection_model.get_all_collections()
    keyboards = [
        [InlineKeyboardButton("مسابقه جدید", "save_qaa")],
    ]
    if collections:
        for id, title, description, is_active in collections:
            button = InlineKeyboardButton(
                title,
                f"action_qaa_collection_menu:{id}:{title}:{description}:{is_active}",
            )
            keyboards.append([button])
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    else:
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])

    return InlineKeyboard(*keyboards)


def index_action_qaa_collection_menu(collection_id, is_active):
    activate_button = (
        [
            InlineKeyboardButton(
                "غیر فعال کردن", f"deactivate_qaa_collection:{collection_id}"
            )
        ]
        if str(is_active) != '0'
        else [
            InlineKeyboardButton(
                "فعال کردن", f"activate_qaa_collection:{collection_id}"
            )
        ]
    )
    return InlineKeyboard(
        activate_button,
        [InlineKeyboardButton("مشاهده نتایج", f"show_qaa_result:{collection_id}")],
        [InlineKeyboardButton("ویرایش عنوان", f"edit_qaa_title:{collection_id}")],
        [
            InlineKeyboardButton(
                "ویرایش توضیحات", f"edit_qaa_description:{collection_id}"
            )
        ],
        [InlineKeyboardButton("پرسش ها", f"index_qaa_collection:{collection_id}")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def index_qaa_question_menu(collection_id):
    questions = qaa_questions_model.get_all_question_by_collection_id(collection_id)
    keyboards = [
        [InlineKeyboardButton("پرسش جدید", f"save_qaa_exam:{collection_id}")],
    ]
    if questions:
        for id, collection_id, question_index, question_text, _, _, _, _ in questions:
            button = InlineKeyboardButton(
                f"{question_index}:{question_text}", f"index_qaa_question:{id}"
            )
            keyboards.append([button])
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])
    else:
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_message")])

    return InlineKeyboard(*keyboards)


def index_action_question_menu(question_id):
    question = qaa_questions_model.get_question_by_id(question_id)
    q_id, collection_id, question_index, text, opt1, opt2, opt3, correct = question

    return InlineKeyboard(
        [InlineKeyboardButton(f"متن: {text}", f"edit_field_qaa:text:{q_id}")],
        [InlineKeyboardButton(f"گزینه 1: {opt1}", f"edit_field_qaa:option1:{q_id}")],
        [InlineKeyboardButton(f"گزینه 2: {opt2}", f"edit_field_qaa:option2:{q_id}")],
        [InlineKeyboardButton(f"گزینه 3: {opt3}", f"edit_field_qaa:option3:{q_id}")],
        [
            InlineKeyboardButton(
                f"گزینه صحیح: {correct}", f"edit_field_qaa:correct:{q_id}"
            )
        ],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def audios_menu():
    rows = audios_model.get_all_audios()
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


def back_to_message_menu():
    return InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_message")])


def back_to_main_menu():
    return InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_main")])
