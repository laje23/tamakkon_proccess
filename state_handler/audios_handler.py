from config import *


async def save_new_audio(message):
    try:
        id = user_temp_data[message.author.id]["audio_id"]
        if id:
            if message.document:
                file_id = message.document.id
                caption = message.caption or ""
                db_audios.update_row_by_id(id, file_id, caption)
                await bale_bot.send_message(
                    message.chat.id, "با موفقیت تغییر کرد ", back_menu()
                )
                message.author.del_state()
            else:
                await bale_bot.send_message(
                    message.chat.id, "فرمت ارسال شده نامعتبر است", back_menu()
                )
        else:
            await bale_bot.send_message(
                message.chat.id, "مشکلی در دریافت ایدی بود ", back_menu()
            )
    except Exception as e:
        await bale_bot.send_message(message.chat.id, e, back_menu())
