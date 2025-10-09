from config import *
from typing import Literal
import json
from utils import (
    success_response,
    error_response,
    get_media_bytes,
    file_id_to_bynery,
    get_mentioning_day,
    split_text_with_index,
    prepare_processed_messages,
)


async def send_to_debugger(result, success=False):
    target = debugger_id
    message = (
        result.get("message", "پیام نامشخص")
        if isinstance(result, dict)
        else str(result)
    )
    if success or (isinstance(result, dict) and not result.get("success", True)):
        try:
            await bale_bot.send_message(target, message)
        except Exception as e:
            pass


async def auto_send_hadith():
    result = db_hadith.return_auto_content()
    if not result:
        return error_response("هیچ پیامی موجود نیست")

    content, id = result

    try:
        await bale_bot.send_message(
            bale_channel_id, process_hadith_message(content, id)
        )
        await eitaa_bot.send_message(
            eitaa_channel_id, process_hadith_message(content, id)
        )
        db_hadith.mark_sent(id)
        return success_response("حدیث ارسال شد")
    except Exception as e:
        return error_response("ارور در ارسال حدیث", e)


async def auto_send_not():
    result = db_notes.get_unsent_note()
    if not result:
        return error_response("هیچ پیامی موجود نیست")

    text_id, file_id, media_type = result
    parts = db_notes.get_parts(text_id)
    if not parts:
        return error_response("هیچ بخشی از متن موجود نیست")

    # اینجا دیگه متن‌ها آماده نهایی ساخته می‌شن
    messages = prepare_processed_messages(parts, text_id)

    try:
        if file_id and media_type:
            file = await file_id_to_bynery(file_id, bale_bot)

            if media_type == "photo":
                await bale_bot.send_photo(bale_channel_id, file.read(), messages[0])
            elif media_type == "video":
                await bale_bot.send_video(bale_channel_id, file.read(), messages[0])

            await eitaa_bot.send_file(eitaa_channel_id, file, messages[0])
            messages.pop(0)

        for msg in messages:
            await bale_bot.send_message(bale_channel_id, msg)
            await eitaa_bot.send_message(eitaa_channel_id, msg)

        db_notes.mark_sent(text_id)
        return success_response("یادداشت ارسال شد")

    except Exception as e:
        return error_response("ارور در ارسال یادداشت", e)


async def send_message_to_channel(message, bot):
    if x := await get_media_bytes(message, bot):
        bin_file, typefile = x
        try:
            if typefile == "photo":
                await bale_bot.send_photo(bale_channel_id, bin_file, message.caption)
            elif typefile == "video":
                await bale_bot.send_video(bale_channel_id, bin_file, message.caption)
            elif typefile == "audio":
                await bale_bot.send_audio(bale_channel_id, bin_file, message.caption)
            await eitaa_bot.send_file(eitaa_channel_id, bin_file, message.caption)
            return success_response("پیام ارسال شد")
        except Exception as e:
            return error_response("خطا در ارسال پیام", e)
    else:
        text = message.text or message.caption
        try:
            await bale_bot.send_message(bale_channel_id, text)
            await eitaa_bot.send_message(eitaa_channel_id, text)
            return success_response("پیام ارسال شد")
        except Exception as e:
            return error_response("خطا در ارسال پیام متنی", e)


async def send_day_info():
    day = get_mentioning_day()
    text = f"""یک صبح دیگر شروع شد بیاید با خواندن ذکر امروز و اهدای ثواب آن برای تعجیل حضرت حجت (عج)
در ظهور آن حضرت سهیم باشم
امروز {day['name']} تاریخ {day['date']} 
ذکر روز {day['zekr']}"""

    try:
        await asyncio.gather(
            bale_bot.send_photo(bale_channel_id, day["path"], text),
            eitaa_bot.send_file(eitaa_channel_id, day["path"], text),
        )
        return success_response("ذکر روز ارسال شد")
    except Exception as e:
        return error_response("خطا در ارسال ذکر روز", e)


async def send_auto_clip():
    try:
        id, file_id, text = db_clips.auto_return_file_id()
        bin_fil = await file_id_to_bynery(file_id, bale_bot)
        text = (text or "") + "\n\n" + "#کلیپ\n@tamakkon_ir"

        await asyncio.gather(
            bale_bot.send_video(bale_channel_id, bin_fil.read(), caption=text),
            eitaa_bot.send_file(eitaa_channel_id, bin_fil, caption=text),
        )
        db_clips.mark_clip_sent(id)
        return success_response("کلیپ ارسال شد")
    except Exception as e:
        return error_response("خطا در ارسال کلیپ", e)


async def send_auto_book():
    try:
        book = db_books.get_unsent_book()
        if not book:
            return error_response("کتاب جدیدی برای ارسال وجود ندارد")

        text = f"""📖  معرفی کتاب روز

عنوان: {book['title']}
نویسنده: {book['author']}
ناشر: {book['publisher'] or 'ناشر نامشخص'}

معرفی کتاب: 
{book['excerpt'] or '...' }


🌹 اللهم عجل لولیک الفرج 🌹

#معرفی_کتاب
@tamakkon_ir"""
        await asyncio.gather(
            bale_bot.send_message(bale_channel_id, text),
            eitaa_bot.send_message(eitaa_channel_id, text),
        )
        db_books.mark_book_sent(book["id"])
        return success_response("کتاب ارسال شد")
    except Exception as e:
        return error_response("خطا در ارسال کتاب", e)


import asyncio


async def send_prayer(prayer_type: Literal["faraj", "ahd", "tohid"]):
    dict_pr = {"faraj": 1, "ahd": 2, "tohid": 3}
    id_key = dict_pr[prayer_type]
    resault = db_audios.get_file_id_and_caption_by_id(id_key)
    if not resault:
        post = error_response("ارور در دریافت ایدی صوت از دیتابیس")
        await send_to_debugger(post)
        return
    file_id, caption = resault
    bin_file = await file_id_to_bynery(file_id, bale_bot)

    await asyncio.gather(
        bale_bot.send_audio(bale_channel_id, bin_file.read(), caption),
        eitaa_bot.send_file(eitaa_channel_id, bin_file, caption),
    )


async def send_auto_lecture():
    try:
        result = db_lecture.auto_return_lecture()
        if not result:
            return error_response("هیچ سخنرانی آماده ارسال نیست")

        id, file_id, caption = result
        bin_file = await file_id_to_bynery(file_id, bale_bot)
        caption = (caption or "") + "\n\n#سخنرانی\n@tamakkon_ir"

        await asyncio.gather(
            bale_bot.send_audio(bale_channel_id, bin_file.read(), caption=caption),
            eitaa_bot.send_file(eitaa_channel_id, bin_file, caption=caption),
        )
        db_lecture.mark_lecture_sent(id)
        return success_response("سخنرانی ارسال شد")
    except Exception as e:
        return error_response("خطا در ارسال سخنرانی", e)
