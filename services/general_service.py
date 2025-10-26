from utils.decorator import safe_run
from utils.datetime import get_mentioning_day
from utils.response import success_response
from utils.media import file_id_to_bynery, get_media_bytes
from config.channels import bale_channel_id, eitaa_channel_id
from config.bots import bale_bot, eitaa_bot
from models import audios_model
from utils.keyboard import back_menu
import asyncio


class GeneralService:
    def __init__(
        self,
        user_temp_data,
        bale_bot=bale_bot,
        eitaa_bot=eitaa_bot,
        audio_model=audios_model,
    ):
        self.bale_bot = bale_bot
        self.eitaa_bot = eitaa_bot
        self.audio_model = audio_model
        self.user_temp_data = user_temp_data
        self.bale_channel_id = bale_channel_id
        self.eitaa_channel_id = eitaa_channel_id

    @safe_run
    async def send_audio_file(self, file_id, caption=None):
        bin_file = await file_id_to_bynery(file_id, self.bale_bot)
        bin_data = await bin_file.read()  # اصلاح: await کردن read()
        await asyncio.gather(
            self.bale_bot.send_audio(self.bale_channel_id, bin_data, caption),
            self.eitaa_bot.send_file(self.eitaa_channel_id, bin_file, caption),
        )
        return success_response("فایل صوتی ارسال شد")

    @safe_run
    async def send_photo_with_text(self, photo_path, text):
        await asyncio.gather(
            self.bale_bot.send_photo(self.bale_channel_id, photo_path, text),
            self.eitaa_bot.send_file(self.eitaa_channel_id, photo_path, text),
        )
        return success_response("پیام تصویری ارسال شد")

    @safe_run
    async def send_text_message(self, text):
        await asyncio.gather(
            self.bale_bot.send_message(self.bale_channel_id, text),
            self.eitaa_bot.send_message(self.eitaa_channel_id, text),
        )
        return success_response("پیام متنی ارسال شد")

    @safe_run
    async def send_prayer(self, prayer_type: str):
        dict_pr = {"faraj": 1, "ahd": 2, "tohid": 3}
        id_key = dict_pr[prayer_type]
        result = self.audio_model.get_file_id_and_caption_by_id(id_key)
        if not result:
            raise Exception("ارور در دریافت ایدی صوت از دیتابیس")

        file_id, caption = result
        await self.send_audio_file(file_id, caption)
        return success_response("دعا ارسال شد")

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
        return success_response("اطلاعات روز ارسال شد ")

    @safe_run
    async def send_message_to_channel(self, message, bot):
        if x := await get_media_bytes(message, bot):
            bin_file, typefile = x
            if typefile == "photo":
                await self.bale_bot.send_photo(self.bale_channel_id, bin_file, message.caption)
            elif typefile == "video":
                await self.bale_bot.send_video(self.bale_channel_id, bin_file, message.caption)
            elif typefile == "audio":
                await self.bale_bot.send_audio(self.bale_channel_id, bin_file, message.caption)
            await self.eitaa_bot.send_file(self.eitaa_channel_id, bin_file, message.caption)
            return success_response("پیام ارسال شد")
        else:
            text = message.text or message.caption
            await self.send_text_message(text)
            return success_response("پیام ارسال شد")

    @safe_run
    async def save_new_audio(self, message):
        user_id = message.author.id
        id = self.user_temp_data[user_id]["audio_id"]
        if id:
            if message.document:
                file_id = message.document.id
                caption = message.caption or ""
                self.audio_model.update_row_by_id(id, file_id, caption)
                await self.bale_bot.send_message(
                    message.chat.id, "با موفقیت تغییر کرد ", back_menu()
                )
                message.author.del_state()
                self.user_temp_data.pop(user_id, None)
            else:
                await self.bale_bot.send_message(
                    message.chat.id, "فرمت ارسال شده نامعتبر است", back_menu()
                )
        else:
            await self.bale_bot.send_message(
                message.chat.id, "مشکلی در دریافت ایدی بود ", back_menu()
            )
