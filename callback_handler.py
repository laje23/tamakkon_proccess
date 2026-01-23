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
    qaa_result_model,
)
from config.service_configs import *
from utils.schaduler_utils import get_schaduler_state, set_schaduler_state
import random


async def call_handler(callback_query):
    t = callback_query.data
    ci = callback_query.message.chat.id
    mi = callback_query.message.id
    ui = callback_query.author.id

    # 🏠 بازگشت به منوی اصلی
    if t == "back_to_main":
        await bale_bot.edit_message_text(
            ci, mi, "سلام! یکی از گزینه‌ها رو انتخاب کن:", main_menu(ui)
        )

    elif t == "qaa_collection_to_user":
        await bale_bot.edit_message_text(
            ci,
            mi,
            " یکی از مسابقات رو انتخاب کن تا اون رو انجام بدی",
            qaa_to_users_menu(),
        )

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
        await bale_bot.edit_message_text(ci, mi, text, back_to_message_menu())

    # 🔄 ارسال خودکار
    elif t == "auto_send_hadith":
        await bale_bot.edit_message_text(ci, mi, "در حال ارسال...")
        result = await hadith_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_to_message_menu())

    elif t == "auto_send_note":
        await bale_bot.edit_message_text(ci, mi, "در حال ارسال...")
        result = await note_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_to_message_menu())

    elif t == "auto_send_clip":
        result = await clip_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_to_message_menu())

    elif t == "auto_send_book":
        result = await book_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_to_message_menu())

    # 🧾 ذخیره یادداشت
    elif t == "save_note":
        callback_query.author.set_state("INPUT_NUMBER_NOTE")
        await bale_bot.send_message(
            ci, "شماره یادداشت رو وارد کنید", back_to_message_menu()
        )

    # ✏️ ویرایش یادداشت
    elif t == "edit_note":
        callback_query.author.set_state("INPUT_EDIT_NUMBER_NOTE")
        await bale_bot.send_message(
            ci, "شماره یادداشت رو وارد کنید", back_to_message_menu()
        )

    # 📚 ذخیره کتاب
    elif t == "save_book":
        callback_query.author.set_state("INPUT_BOOK_TITLE")
        await bale_bot.send_message(
            ci, "عنوان کتاب رو وارد کنید", back_to_message_menu()
        )

    # ✏️ ویرایش کتاب
    elif t == "edit_book":
        callback_query.author.set_state("EDIT_BOOK_ID")
        await bale_bot.send_message(
            ci, "شناسه کتاب رو وارد کنید", back_to_message_menu()
        )

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
            await bale_bot.edit_message_text(
                ci, mi, "زمانبندی فعال شد", back_to_message_menu()
            )

        elif t == "schaduler_off":
            set_schaduler_state(False)
            await bale_bot.edit_message_text(
                ci, mi, "زمانبندی غیرفعال شد", back_to_message_menu()
            )

    elif t == "auto_send_lecture":
        result = await lecture_services.auto_send()
        await bale_bot.send_message(ci, result["message"], back_to_message_menu())

    elif t == "add_and_edit":
        await bale_bot.edit_message_text(ci, mi, "وضعیت زمانبندی", save_or_edit_menu())

    elif t == "clip_menu":
        callback_query.author.set_state("INPUT_NEW_CLIP")
        await bale_bot.edit_message_text(
            ci, mi, "کلیپ رو ارسال کنید", back_to_message_menu()
        )

    elif t.startswith("audio"):
        callback_query.author.set_state("INPUT_AUDIO_FILE")
        await bale_bot.send_message(
            ci, "لطفا صوت جدید را وارد کنید", back_to_message_menu()
        )
        id = t.split(":")[1].strip()
        user_temp_data[ui] = {"audio_id": id}

    elif t == "create_default_audios_row":
        audio_name_list = ["دعای فرج", "دعای احد", "توحید"]
        for i in audio_name_list:
            audios_model.insert_audio(str(i), 0000000, "")
        await bale_bot.edit_message_text(
            ci, mi, "مقادیر پیشفرض ایجاد شدند", back_to_message_menu()
        )

    elif t == "save_qaa":
        await bale_bot.send_message(
            ci, "عنوان مسابقه جدید را ارسال کنید", back_to_message_menu()
        )
        callback_query.author.set_state("ENTER_QAA_TITLE")

    elif t == "qaa_menu":
        await bale_bot.edit_message_text(ci, mi, "منوی مسابقات", qaa_menu())

    elif t.startswith("index_qaa_collection:"):
        id = t.split(":")[1].strip()
        id, title, description, is_activ = qaa_collection_model.get_collection(id)
        status = "فعال" if is_activ == 1 else "غیرفعال"
        await bale_bot.edit_message_text(
            ci,
            mi,
            f"عنوان:{title} \n\n توضیحات: {description}\n\nوضعیت: {status}",
            index_qaa_question_menu(id),
        )

    elif t.startswith("save_qaa_exam"):
        id = t.split(":")[1].strip()
        await qaa_service.save_qaa_state_1(callback_query.author, id)

    elif t.startswith("action_qaa_collection_menu"):
        _, id, title, description, is_active = t.split(":")
        await bale_bot.edit_message_text(
            ci,
            mi,
            f"عنوان: {title} \n\nتوضیحات: {description} \n\n لطفا یک گزینه را انتخاب کنید",
            index_action_qaa_collection_menu(id, is_active),
        )

    elif t.startswith("edit_qaa_title"):
        id = t.split(":")[1].strip()
        await qaa_service.edit_qaa_tilt_1(callback_query.author, id)

    elif t.startswith("edit_qaa_description"):
        id = t.split(":")[1].strip()
        await qaa_service.edit_qaa_description_1(callback_query.author, id)

    elif t.startswith("index_qaa_question"):
        id = t.split(":")[1].strip()
        await bale_bot.edit_message_text(
            ci,
            mi,
            "لطفا یک گزینه را برای ویرایش انتخاب کنید",
            index_action_question_menu(id),
        )

    elif t.startswith("edit_field"):
        _, field, qid = t.split(":")
        await qaa_service.start_edit_field(callback_query.author, qid, field)

    elif t == "login":
        await user_service.handel_login_button(callback_query.author, mi)

    elif t.startswith("deactivate_qaa_collection"):
        collection_id = t.split(":")[1].strip()
        qaa_collection_model.deactivate_collection(collection_id)
        await bale_bot.edit_message_text(
            ci,
            mi,
            "مسابقه مورد نظر غیر فعال شد",
            back_to_message_menu(),
        )

    elif t.startswith("activate_qaa_collection"):
        collection_id = t.split(":")[1].strip()
        qaa_collection_model.activate_collection(collection_id)
        await bale_bot.edit_message_text(
            ci,
            mi,
            "مسابقه مورد نظر فعال شد",
            back_to_message_menu(),
        )

    elif t.startswith("qaa_doing_user"):
        collection_id = t.split(":")[1].strip()
        result = qaa_result_model.get_collection_results(collection_id)
        for _, user_id, _, _ in result:
            if ui == user_id:
                await bale_bot.edit_message_text(
                    ci, mi, "شما این مسابقه را قبلا انجام داده اید", back_to_main_menu()
                )
                return

        await qaa_service.do_qaa_conf(callback_query.author, mi, collection_id)

    elif t.startswith("qaa_answer"):
        answer = t.split(":")[1].strip()
        await qaa_service.handel_qaa_answers(callback_query.author, mi, answer)

    elif t.startswith("show_qaa_result"):
        collection_id = t.split(":")[1].strip()
        result = qaa_result_model.get_collection_results(collection_id)
        text = "اسامی شرکت کنندگان \n\n"
        for id, user_id, collection_id, is_winner in result:
            _, user_id, name, _, _ = user_model.get_user(user_id)
            win = "موفق" if is_winner == 1 else "ناموفق"
            text = text + f"{name} با شماره {user_id} در این مسابقه {win} بود\n"

        await bale_bot.edit_message_text(ci, mi, text, chose_winner_for_qaa_menu(collection_id))
        
    elif t.startswith('chose_random_winner'):
        collection_id = t.split(':')[-1].strip()
        result = qaa_result_model.get_collection_winners(collection_id)
        _, user_id, _, _ = random.choice(result)
        _, _, name, _, _ = user_model.get_user(user_id)
        text = f'آقا/خانم {name} با شماره آیدی {user_id}'
        
        await bale_bot.edit_message_text(ci, mi, text, back_to_message_menu())
