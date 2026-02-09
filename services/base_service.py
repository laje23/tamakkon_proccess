# services/base_service.py
from utils.decorator import safe_run
from utils.response import success_response
from config.channels import bale_channel_id, eitaa_channel_id


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
    async def send_media(self, media_type, bin_file, caption=None):
        """
        ارسال رسانه به کانال‌های بله و ایتا
        media_type: 'photo' | 'video' | 'audio'
        bin_file: bytes یا BinaryIO
        caption: متن همراه
        """

        platforms = {
            "bale": {"func": None, "channel": self.bale_channel_id},
            "eitaa": {"func": None, "channel": self.eitaa_channel_id},
        }

        # انتخاب تابع ارسال بر اساس نوع رسانه
        if media_type == "photo":
            bale_send = self.bale_bot.send_photo
            eitaa_send = self.eitaa_bot.send_file
        elif media_type == "video":
            bale_send = self.bale_bot.send_video
            eitaa_send = self.eitaa_bot.send_file
        elif media_type == "audio":
            bale_send = self.bale_bot.send_audio
            eitaa_send = self.eitaa_bot.send_file
        else:
            raise Exception("فرمت فایل نا معتبر")
        

        # ارسال به بله
        if hasattr(bin_file, "seek"):
            bin_file.seek(0)
        await bale_send(self.bale_channel_id, bin_file.read(), caption=caption)

        # ارسال به ایتا
        if hasattr(bin_file, "seek"):
            bin_file.seek(0)
        await eitaa_send(self.eitaa_channel_id, bin_file, caption)

        return success_response(f"{media_type} ارسال شد به همه پلتفرم‌ها")
