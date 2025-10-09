# services/general_service.py

from utils.decorator import safe_run
from utils.datatime import get_mentioning_day
from utils.respons import success_response
from utils.media import file_id_to_bynery, get_media_bytes
from config.channels import bale_channel_id, eitaa_channel_id
from config.bots import bale_bot, eitaa_bot
from models import audio_model
from utils.keyboard import back_menu
import asyncio


class GeneralService:
    def __init__(
        self,
        user_temp_data,
        bale_bot=bale_bot,
        eitaa_bot=eitaa_bot,
        audio_model=audio_model,
    ):
        self.bale_bot = bale_bot
        self.eitaa_bot = eitaa_bot
        self.audio_model = audio_model
        self.user_temp_data = user_temp_data

    @safe_run
    async def send_audio_file(self, file_id, caption=None):
        bin_file = await file_id_to_bynery(file_id, self.bale_bot)
        await asyncio.gather(
            self.bale_bot.send_audio(bale_channel_id, bin_file.read(), caption),
            self.eitaa_bot.send_file(eitaa_channel_id, bin_file, caption),
        )
        return success_response("فایل صوتی ارسال شد")

    @safe_run
    async def send_photo_with_text(self, photo_path, text):
        await asyncio.gather(
            self.bale_bot.send_photo(bale_channel_id, photo_path, text),
            self.eitaa_bot.send_file(eitaa_channel_id, photo_path, text),
        )
        return success_response("پیام تصویری ارسال شد")

    @safe_run
    async def send_text_message(self, text):
        await asyncio.gather(
            self.bale_bot.send_message(bale_channel_id, text),
            self.eitaa_bot.send_message(eitaa_channel_id, text),
        )
        return success_response("پیام متنی ارسال شد")

    # مثال: ارسال اذکار روز
    @safe_run
    async def send_prayer(self, prayer_type: str):
        dict_pr = {"faraj": 1, "ahd": 2, "tohid": 3}
        id_key = dict_pr[prayer_type]
        result = self.audio_model.get_file_id_and_caption_by_id(id_key)
        if not result:
            raise Exception("ارور در دریافت ایدی صوت از دیتابیس")

        file_id, caption = result
        await self.send_audio_file(file_id, caption)

    # مثال: ارسال ذکر روز
    @safe_run
    async def send_day_info(self):
        day = get_mentioning_day()
        text = (
            f"یک صبح دیگر شروع شد بیاید با خواندن ذکر امروز و اهدای ثواب آن "
            f"برای تعجیل حضرت حجت (عج)\n"
            f"امروز {day['name']} تاریخ {day['date']}\n"
            f"ذکر روز {day['zekr']}"
        )
        await self.send_photo_with_text(day["path"], text)

    @safe_run
    async def send_message_to_channel(self, message, bot):
        if x := await get_media_bytes(message, bot):
            bin_file, typefile = x
            if typefile == "photo":
                await bale_bot.send_photo(bale_channel_id, bin_file, message.caption)
            elif typefile == "video":
                await bale_bot.send_video(bale_channel_id, bin_file, message.caption)
            elif typefile == "audio":
                await bale_bot.send_audio(bale_channel_id, bin_file, message.caption)
            await eitaa_bot.send_file(eitaa_channel_id, bin_file, message.caption)
            return success_response("پیام ارسال شد")
        else:
            text = message.text or message.caption
            await self.send_text_message(text)
            return success_response("پیام ارسال شد")

    @safe_run
    async def save_new_audio(self, message):
        id = self.user_temp_data[message.author.id]["audio_id"]
        if id:
            if message.document:
                file_id = message.document.id
                caption = message.caption or ""
                self.audio_model.update_row_by_id(id, file_id, caption)
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
