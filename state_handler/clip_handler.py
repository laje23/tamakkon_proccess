from config import *

MESSAGES = {
    "invalid_number": "❗️ لطفاً فقط عدد مثبت وارد کنید.",
    "only_number": "لطفاً فقط عدد وارد کن.",
    "clip_not_found": "❌ کلیپی با این شناسه پیدا نشد.",
    "clip_already_sent": "❌ این کلیپ قبلاً ارسال شده و قابل ویرایش نیست.",
    "enter_id": "شماره کلیپ را وارد کنید:",
    "send_clip": "لطفا کلیپ را ارسال کنید.",
    "send_caption": "کپشن کلیپ را ارسال کن:",
    "clip_caption_saved": "✅ کلیپ و کپشن با موفقیت ذخیره شدند.",
    "enter_new_caption": "کپشن جدید را ارسال کنید:",
    "caption_edited": "✅ کپشن کلیپ با موفقیت ویرایش شد.",
    "error_editing_caption": "❌ خطا در ویرایش کپشن:",
}


# مرحله دوم - دریافت کلیپ
async def handle_new_clip(message):
    user_id = message.author.id
    user_temp_data[user_id] = {}

    if message.video:
        clip_file_id = message.video.id
    else:
        await bale_bot.send_message(message.chat.id, MESSAGES["send_clip"])
        return

    user_temp_data[user_id]["clip_file_id"] = clip_file_id
    message.author.set_state("INPUT_CLIP_CAPTION")
    await bale_bot.send_message(message.chat.id, MESSAGES["send_caption"])


# مرحله سوم - دریافت کپشن و ذخیره نهایی کلیپ جدید
async def handle_clip_caption(message):
    user_id = message.author.id
    file_id = user_temp_data[user_id].get("clip_file_id")
    caption = message.text.strip()

    try:
        db_clips.save_clip(file_id, caption)
        await bale_bot.send_message(
            message.chat.id, MESSAGES["clip_caption_saved"], back_menu()
        )
    except Exception as e:
        await bale_bot.send_message(
            message.chat.id, f"❌ خطا در ذخیره: {str(e)}", back_menu()
        )

    user_temp_data.pop(user_id, None)
    message.author.del_state()


# مرحله ویرایش کپشن
async def handle_edit_caption(message):
    user_id = message.author.id
    id = user_temp_data[user_id].get("edit_id")
    new_caption = message.text.strip()

    try:
        db_clips.edit_clip_caption(id, new_caption)
        await bale_bot.send_message(
            message.chat.id, MESSAGES["caption_edited"], back_menu()
        )
    except Exception as e:
        await bale_bot.send_message(
            message.chat.id,
            f"{MESSAGES['error_editing_caption']} {str(e)}",
            back_menu(),
        )

    user_temp_data.pop(user_id, None)
    message.author.del_state()
