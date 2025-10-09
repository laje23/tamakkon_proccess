# services/base_service.py

from utils.decorator import safe_run
from utils.respons import success_response
from config.channels import bale_channel_id , eitaa_channel_id

class BaseService:
    def __init__(self, db_model, bale_bot, eitaa_bot):
        self.db = db_model
        self.bale_bot = bale_bot
        self.eitaa_bot = eitaa_bot
        self.bale_channel_id = bale_channel_id
        self.eitaa_channel_id = eitaa_channel_id

    @safe_run
    async def send_text(self, text_bale, text_eitaa):
        """ارسال پیام متنی به هر دو پلتفرم"""
        await self.bale_bot.send_message(self.bale_channel_id, text_bale)
        await self.eitaa_bot.send_message(self.eitaa_channel_id, text_eitaa)
        return success_response("پیام متنی ارسال شد")

    @safe_run
    async def send_media(self, media_type, file_id, caption=None):
        """ارسال عکس، ویدیو یا صوت"""
        if media_type == "photo":
            await self.bale_bot.send_photo(self.bale_channel_id, file_id, caption)
            await self.eitaa_bot.send_file(self.eitaa_channel_id, file_id, caption)
        elif media_type == "video":
            await self.bale_bot.send_video(self.bale_channel_id, file_id, caption)
            await self.eitaa_bot.send_file(self.eitaa_channel_id, file_id, caption)
        elif media_type == "audio":
            await self.bale_bot.send_audio(self.bale_channel_id, file_id, caption)
            await self.eitaa_bot.send_file(self.eitaa_channel_id, file_id, caption)
        else:
            raise Exception('فرمت فایل نا معتبر')
        return success_response(f"{media_type} ارسال شد")
