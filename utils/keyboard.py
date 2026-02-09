from balethon.objects import InlineKeyboard, InlineKeyboardButton
from models import user_model , media_model
from models import user_permission_model as up_model
from models import permissions_model
from balethon.objects import InlineKeyboard, InlineKeyboardButton
from models import qaa_collection_model, qaa_questions_model, user_model
from models import user_permission_model as up_model
from utils.decorator import require_permission


def main_menu(user_id):
    person = user_model.get_user(user_id)

    if not person:
        rows = [[InlineKeyboardButton("ورود", "login")]]
    else:
        user_db_id, tg_user_id, name, phone_number = person

        # همیشه همه می‌بینن
        rows = [[InlineKeyboardButton("مسابقات", "qaa_collection_to_user")]]

        # فقط افرادی که permission مدیریت پیام‌ها دارند
        if up_model.has_permission(user_db_id, "view_bot_management_menu"):
            rows.append([InlineKeyboardButton("مدیریت پیام‌ها", "back_to_message")])

    return InlineKeyboard(*rows)


@require_permission("view_bot_management_menu")
def message_menu(user_id):
    return InlineKeyboard(
        [InlineKeyboardButton("ارسال ها", "send_menu")],
        [InlineKeyboardButton("مسابقات", "qaa_menu")],
        [InlineKeyboardButton("ذخیره و ویرایش", "add_and_edit")],
        [InlineKeyboardButton("صوت های ارسالی", "change_audio_file_id")],
        [InlineKeyboardButton("دسترسی ها", "back_to_users_list")],
        [InlineKeyboardButton("گرفتن آمار", "get_status")],
        [InlineKeyboardButton("زمانبندی", "schaduler_menu")],
        [InlineKeyboardButton("بازگشت", "back_to_main")],
    )


def qaa_to_users_menu():
    collections = qaa_collection_model.get_pos_collections(active=True)
    keyboards = []
    if collections:
        for id, title, description in collections:
            button = InlineKeyboardButton(title, f"qaa_doing_user:{id}")
            keyboards.append([button])
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_main")])
    else:
        keyboards.append([InlineKeyboardButton("بازگشت", "back_to_main")])

    return InlineKeyboard(*keyboards)


@require_permission("competition_Management")
def qaa_menu(user_id):
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
        if str(is_active) != "0"
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


@require_permission("manage_default_sounds")
def audios_menu(user_id):
    rows = media_model.get_all_audios()
    keyboards = []
    if rows:
        for row in rows:
            id, file_name, file_id, caption, sent = row
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


@require_permission("toggle_scheduling_mode")
def schaduler_menu(on: bool, user_id):
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


@require_permission("save_and_edit_content")
def save_or_edit_menu(user_id):
    return InlineKeyboard(
        [InlineKeyboardButton("یادداشت", "note_menu")],
        [InlineKeyboardButton("کتاب", "book_menu")],
        [InlineKeyboardButton("کلیپ", "clip_menu")],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


@require_permission("send_to_channel")
def send_menu(user_id):
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


def chose_winner_for_qaa_menu(collection_id):
    return InlineKeyboard(
        [
            InlineKeyboardButton(
                "یک برنده را به طور تصادفی انتخاب کن",
                f"chose_random_winner:{collection_id}",
            )
        ],
        [InlineKeyboardButton("بازگشت", "back_to_message")],
    )


def back_to_message_menu():
    return InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_message")])


def back_to_main_menu():
    return InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_main")])


@require_permission("member_access_management")
def users_menu(user_id, page=0, callback_data=""):
    users = user_model.get_all_users()
    total_users = len(users)
    start = page * 10
    end = start + 10
    page_users = users[start:end]

    keyboards = []

    # دکمه‌های کاربران
    for user in page_users:
        user_db_id, user_id, name, phone_number = user
        keyboards.append([InlineKeyboardButton(name, f"{callback_data}:{user_id}")])

    # دکمه‌های صفحه قبل و بعد
    nav_buttons = []

    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ صفحه قبل", f"users_page:{page-1}"))

    if end < total_users:
        nav_buttons.append(InlineKeyboardButton("➡️ صفحه بعد", f"users_page:{page+1}"))

    if nav_buttons:
        keyboards.append(nav_buttons)

    # دکمه برگشت
    keyboards.append([InlineKeyboardButton("بازگشت", "back_to_main")])

    return InlineKeyboard(*keyboards)


@require_permission("member_access_management")
def user_permissions_menu(user_id, page=0):
    """
    منوی permissionهای یک کاربر
    :param user_id: user_id تلگرام یا دیتابیس (بسته به اینکه db_id داری یا نه)
    :param page: شماره صفحه برای pagination
    """
    rows = []

    # گرفتن اطلاعات کاربر
    user_info = user_model.get_user(user_id)
    if not user_info:
        return InlineKeyboard(
            [InlineKeyboardButton("❌ کاربر یافت نشد", "back_to_main")]
        )

    db_id = user_info[0]

    # گرفتن همه permissionها
    all_permissions = permissions_model.get_all_permissions()  # [(id, code, desc), ...]
    user_permissions = [
        p[0] for p in up_model.get_user_permissions(db_id)
    ]  # ['auto_send', ...]

    # صفحه بندی
    start = page * 10
    end = start + 10
    page_permissions = all_permissions[start:end]

    for perm_id, code, desc in page_permissions:
        # مشخص می‌کنیم کاربر این permission را دارد یا نه
        label = f"✅ {code}" if code in user_permissions else f"❌ {code}"
        callback_data = f"toggle_permission:{user_id}:{db_id}:{code}"
        rows.append([InlineKeyboardButton(label, callback_data)])

    # دکمه‌های صفحه قبل / بعد
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                "⬅️ صفحه قبل", f"user_permissions_page:{user_id}:{page-1}"
            )
        )
    if end < len(all_permissions):
        nav_buttons.append(
            InlineKeyboardButton(
                "➡️ صفحه بعد", f"user_permissions_page:{user_id}:{page+1}"
            )
        )
    if nav_buttons:
        rows.append(nav_buttons)

    # دکمه برگشت
    rows.append([InlineKeyboardButton("بازگشت", f"back_to_users_list")])

    return InlineKeyboard(*rows)
