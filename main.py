from balethon.conditions import command, group, at_state, private, all
from models import hadith_model, lectures_model
from config.bots import bale_bot
from config.admins import admins
from utils.notifiter import send_to_admins
from config.channels import group_reserch_hadith_id, group_reserch_lecture_id
from utils.keyboard import *
from utils.response import *
from dotenv import load_dotenv
from schaduler import scheduled_messages
from config.service_configs import (
    note_services,
    general_services,
    book_services,
    qaa_service,
    clip_services,
)
import threading
import callback_handler as call
import asyncio

load_dotenv()


@bale_bot.on_callback_query(at_state("DOING_ANSWERS"))
async def handle_qaa_answer_buttons(callback_query):
    await qaa_service.handel_qaa_answers(
        callback_query.author, callback_query.message.id, callback_query.data
    )


# 🎯 هندل کردن دکمه‌های callback
@bale_bot.on_callback_query(private)
async def reply_buttons(callback_query):
    await call.call_handler(callback_query)


# 🚀 شروع ربات
@bale_bot.on_message(command("start") & private)
async def handle_start(message):
    is_admin = message.author.id in admins
    await bale_bot.send_message(
        message.chat.id,
        "سلام! یکی از گزینه‌ها رو انتخاب کنید:",
        main_menu(is_admin),
    )


# 📝 ذخیره یادداشت
@bale_bot.on_message(at_state("INPUT_NUMBER_NOTE"))
async def first_state_save_note(message):
    await note_services.first_step_save(message)


@bale_bot.on_message(at_state("INPUT_TEXT_NOTE"))
async def next_state_save_note(message):
    await note_services.handle_text_parts(message)  # تغییر داده شد به handle_text_parts


# ✏️ ویرایش یادداشت
@bale_bot.on_message(at_state("INPUT_EDIT_NUMBER_NOTE"))
async def first_state_edit_note(message):
    await note_services.first_step_save(message)  # اگر تابع مشابه first_step_save است


@bale_bot.on_message(at_state("INPUT_EDIT_TEXT_NOTE"))
async def next_state_edit_note(message):
    await note_services.handle_text_parts(message)  # مجدداً همان تابع handle_text_parts


@bale_bot.on_message(at_state("CONFIRM_MORE_TEXT"))
async def confirm_more_text_handler(message):
    await note_services.confirm_more_text(message)


# 📎 دریافت فایل یا پاسخ 'ندارم' قبل از گرفتن متن یادداشت
@bale_bot.on_message(at_state("ASK_MEDIA"))
async def handle_media_state(message):
    await note_services.handle_media_step(message)


# 📢 ارسال پیام به کانال
@bale_bot.on_message(at_state("SEND_MESSAGE_TO_CHANEL") & all)
async def send_to_channel(message):
    sent = await bale_bot.send_message(message.chat.id, "در حال ارسال ...")
    text = await general_services.send_message_to_channel(message, bale_bot)
    message.author.del_state()
    await bale_bot.edit_message_text(sent.chat.id, sent.id, text, back_menu())


@bale_bot.on_message(at_state("INPUT_BOOK_TITLE"))
async def handle_book_title(message):
    await book_services.input_book_title(message)


@bale_bot.on_message(at_state("INPUT_BOOK_AUTHOR"))
async def handle_book_author(message):
    await book_services.input_book_author(message)


@bale_bot.on_message(at_state("INPUT_BOOK_PUBLISHER"))
async def handle_book_publisher(message):
    await book_services.input_book_publisher(message)


@bale_bot.on_message(at_state("INPUT_BOOK_EXCERPT"))
async def handle_book_excerpt(message):
    await book_services.input_book_excerpt(message)


@bale_bot.on_message(at_state("EDIT_BOOK_ID"))
async def handle_book_id_edit(message):
    await book_services.input_book_id_for_edit(message)


@bale_bot.on_message(at_state("EDIT_BOOK_TITLE"))
async def handle_book_title_edit(message):
    await book_services.input_new_title(message)


@bale_bot.on_message(at_state("EDIT_BOOK_AUTHOR"))
async def handle_book_author_edit(message):
    await book_services.input_new_author(message)


@bale_bot.on_message(at_state("EDIT_BOOK_PUBLISHER"))
async def handle_book_publisher_edit(message):
    await book_services.input_new_publisher(message)


@bale_bot.on_message(at_state("EDIT_BOOK_EXCERPT"))
async def handle_book_excerpt_edit(message):
    await book_services.input_new_excerpt(message)


@bale_bot.on_message(at_state("INPUT_NEW_CLIP"))
async def _(message):
    await clip_services.handle_new_clip(message)


@bale_bot.on_message(at_state("INPUT_CLIP_CAPTION"))
async def _(message):
    await clip_services.handle_clip_caption(message)


@bale_bot.on_message(at_state("EDIT_CLIP_CAPTION"))
async def _(message):
    await clip_services.handle_edit_caption(message)


@bale_bot.on_message(at_state("INPUT_AUDIO_FILE"))
async def _(message):
    await clip_services.save_new_audio(message)


# ⏳ مرحله اول – دریافت عنوان کالکشن
@bale_bot.on_message(at_state("ENTER_QAA_TITLE"))
async def handle_qaa_title(message):
    await qaa_service.save_qaa_title(message.author, message.text)


# 📝 مرحله دوم – دریافت متن سوال
@bale_bot.on_message(at_state("ENTER_QAA_TEXT"))
async def handle_qaa_question_text(message):
    await qaa_service.save_qaa_state_2(message.author, message.text)


# ❌ مرحله چهارم – جواب غلط ۲
@bale_bot.on_message(at_state("ENTER_QAA_QUESTION_1"))
async def handle_qaa_wrong_1(message):
    await qaa_service.save_qaa_state_3(message.author, message.text)


# ❌ مرحله چهارم – جواب غلط ۲
@bale_bot.on_message(at_state("ENTER_QAA_QUESTION_2"))
async def handle_qaa_wrong_2(message):
    await qaa_service.save_qaa_state_4(message.author, message.text)


# ❌ مرحله پنجم – جواب غلط ۳
@bale_bot.on_message(at_state("ENTER_QAA_QUESTION_3"))
async def handle_qaa_wrong_3(message):
    await qaa_service.save_qaa_state_5(message.author, message.text)


# ✅ مرحله ششم – جواب درست
@bale_bot.on_message(at_state("ENTER_QAA_CORRECT_OPTION"))
async def handle_qaa_correct(message):
    await qaa_service.save_qaa_state_6(message.author, message.text)


@bale_bot.on_message(at_state("EDIT_QAA_TITLE"))
async def handle_qaa_edit_title(message):
    await qaa_service.edit_qaa_title_2(message.author, message.text)


@bale_bot.on_message(at_state("EDIT_QAA_DESCRIPTION"))
async def handle_qaa_edit_description(message):
    await qaa_service.edit_qaa_description_2(message.author, message.text)


@bale_bot.on_message(at_state("EDIT_QAA_FIELD"))
async def handle_qaa_field_edit(message):
    await qaa_service.commit_edit_field(message.author, message.text)


# 📥 دریافت پیام‌های گروهی
@bale_bot.on_message(group)
async def collect_group_input(message):
    try:
        if message.chat.id == group_reserch_hadith_id:
            hadith_model.save_id_and_content(message.id, message.text)

        elif message.chat.id == group_reserch_lecture_id:
            if message.document:
                lectures_model.save_lecture(message.document.id, message.caption)
            else:
                await send_to_admins(
                    error_response("پیام ارسال شده در گروه سخنرانی فرمتی نامعتبر دارد")
                )

    except Exception as e:
        await send_to_admins(e)


def start_scheduler_loop():
    asyncio.run(scheduled_messages())


threading.Thread(target=start_scheduler_loop, daemon=True).start()

# 🧠 اجرای اصلی ربات
bale_bot.run()
