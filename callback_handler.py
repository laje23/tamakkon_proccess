from utils.keyboard import *
from config.admins import admins
from config.setting import user_temp_data
from config.bots import bale_bot
from models import (
    audios_model,
    books_model,
    hadith_model,
    lectures_model,
    notes_model,
    clips_model,
    qaa_collection_model,
)
from config.service_configs import *
from utils.schaduler_utils import get_schaduler_state, set_schaduler_state


async def call_handler(callback_query):
    t = callback_query.data
    ci = callback_query.message.chat.id
    mi = callback_query.message.id
    ui = callback_query.author.id

    # 🏠 بازگشت به منوی اصلی
    if t == "back_to_main":
        await bale_bot.edit_message_text(
            ci, mi, "سلام! یکی از گزینه‌ها رو انتخاب کن:", main_menu(ui in admins)
        )

    elif t == "in_update":
        pass

    # 📩 بازگشت به منوی پیام‌ها
    elif t == "back_to_message":
        try:
            callback_query.author.del_state()
        except:
            pass
        await bale_bot.edit_message_text(ci, mi, "منوی مدیریت پیام", message_menu())

    # 📤 منوی ارسال
    elif t == "send_menu":
        await bale_bot.edit_message_text(
            ci, mi, "لطفا یک گزینه برای ارسال انتخاب کنید", send_menu()
        )

    elif t == "change_audio_file_id":
        await bale_bot.edit_message_text(
            ci, mi, "یکی را برای تغییر شناسه فایل آن انتخاب کنید ", audios_menu()
        )

    # 📝 منوی یادداشت‌ها
    elif t == "note_menu":
        await bale_bot.edit_message_text(
            ci, mi, "لطفا یک گزینه را انتخاب کنید", note_menu()
        )

    # 📚 منوی کتاب‌ها
    elif t == "book_menu":
        await bale_bot.edit_message_text(ci, mi, "منوی معرفی کتاب", book_menu())

    # 📊 دریافت آمار
    elif t == "get_status":
        book = books_model.get_status()
        clip = clips_model.get_status()
        hadith = hadith_model.get_status()
        note = notes_model.get_status()
        lecture = lectures_model.get_status()

        text = f"""آمار کلی سیستم:
.............................
کتاب‌ها
    ارسال شده: {book['sent']}
    ارسال نشده: {book['unsent']}

کلیپ‌ها
    ارسال شده: {clip['sent']}
    ارسال نشده: {clip['unsent']}

احادیث
    ارسال شده: {hadith['sent']}
    ارسال نشده: {hadith['unsent']}

یادداشت‌ها
    ارسال شده: {note['sent']}
    ارسال نشده: {note['unsent']}

سخنرانی ها 
    ارسال شده: {lecture['sent']}
    ارسال نشده: {lecture['unsent']}
"""
        await bale_bot.edit_message_text(ci, mi, text, back_menu())

    # 🔄 ارسال خودکار
    elif t == "auto_send_hadith":
        await bale_bot.edit_message_text(ci, mi, "در حال ارسال...")
        result = await hadith_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_menu())

    elif t == "auto_send_note":
        await bale_bot.edit_message_text(ci, mi, "در حال ارسال...")
        result = await note_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_menu())

    elif t == "auto_send_clip":
        result = await clip_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_menu())

    elif t == "auto_send_book":
        result = await book_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_menu())

    # 🧾 ذخیره یادداشت
    elif t == "save_note":
        callback_query.author.set_state("INPUT_NUMBER_NOTE")
        await bale_bot.send_message(ci, "شماره یادداشت رو وارد کنید", back_menu())

    # ✏️ ویرایش یادداشت
    elif t == "edit_note":
        callback_query.author.set_state("INPUT_EDIT_NUMBER_NOTE")
        await bale_bot.send_message(ci, "شماره یادداشت رو وارد کنید", back_menu())

    # 📚 ذخیره کتاب
    elif t == "save_book":
        callback_query.author.set_state("INPUT_BOOK_TITLE")
        await bale_bot.send_message(ci, "عنوان کتاب رو وارد کنید", back_menu())

    # ✏️ ویرایش کتاب
    elif t == "edit_book":
        callback_query.author.set_state("EDIT_BOOK_ID")
        await bale_bot.send_message(ci, "شناسه کتاب رو وارد کنید", back_menu())

    # 📤 ارسال پیام به کانال
    elif t == "send_to_channel":
        await bale_bot.send_message(ci, "پیام را ارسال یا فوروارد کنید")
        callback_query.author.set_state("SEND_MESSAGE_TO_CHANEL")

    elif t == "schaduler_menu":
        await bale_bot.edit_message_text(
            ci, mi, "وضعیت زمانبندی", schaduler_menu(on=get_schaduler_state())
        )

    elif t.startswith("schaduler"):
        if t == "schaduler_on":
            set_schaduler_state(True)
            await bale_bot.edit_message_text(ci, mi, "زمانبندی فعال شد", back_menu())

        elif t == "schaduler_off":
            set_schaduler_state(False)
            await bale_bot.edit_message_text(ci, mi, "زمانبندی غیرفعال شد", back_menu())

    elif t == "auto_send_lecture":
        result = await lecture_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_menu())

    elif t == "add_and_edit":
        await bale_bot.edit_message_text(ci, mi, "وضعیت زمانبندی", save_or_edit_menu())

    elif t == "clip_menu":
        callback_query.author.set_state("INPUT_NEW_CLIP")
        await bale_bot.edit_message_text(ci, mi, "کلیپ رو ارسال کنید", back_menu())

    elif t.startswith("audio"):
        callback_query.author.set_state("INPUT_AUDIO_FILE")
        await bale_bot.send_message(ci, "لطفا صوت جدید را وارد کنید", back_menu())
        id = t.split(":")[1].strip()
        user_temp_data[ui] = {"audio_id": id}

    elif t == "create_default_audios_row":
        audio_name_list = ["دعای فرج", "دعای احد", "توحید"]
        for i in audio_name_list:
            audios_model.insert_audio(str(i), 0000000, "")
        await bale_bot.edit_message_text(
            ci, mi, "مقادیر پیشفرض ایجاد شدند", back_menu()
        )

    elif t == "qaa_save":
        await bale_bot.send_message(ci, "عنوان پرسش رو وارد کنید")
        callback_query.author.set_state("ENTER_QAA_TITLE")

    elif t == "qaa_menu":
        await bale_bot.edit_message_text(
            ci, mi, "یکی از گزینه ها را انتخاب کنید", qaa_menu()
        )

    elif t == "start_qaa":
        await bale_bot.edit_message_text(
            ci, mi, "یکی از مسابقات را برای شروع آن انتخاب کنید", start_qaa_menu()
        )

    elif t == "end_qaa":
        await bale_bot.edit_message_text(
            ci, mi, "یکی از مسابقات را برای پایان دادن به آن انتخاب کنید", end_qaa_menu()
        )

    elif t.startswith("start_qaa:"):
        id = t.split(":")[1].strip()
        qaa_collection_model.activate_collection(id)
        await bale_bot.edit_message_text(ci, mi, "مسابقه فعال شد", back_menu())

    elif t.startswith("end_qaa:"):
        id = t.split(":")[1].strip()
        qaa_collection_model.deactivate_collection(id)
        await bale_bot.edit_message_text(ci, mi, "مسابقه غیر فعال شد", back_menu())
