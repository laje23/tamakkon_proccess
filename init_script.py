from models import (
    audio_model,
    books_model,
    clips_model,
    hadith_model,
    lecture_model,
    notes_model,
)
from config.channels import eitaa_channel_id_test
from config.bots import eitaa_bot
import asyncio


if __name__ == "__main__":
    lecture_model.create_table()
    clips_model.create_table()
    notes_model.create_table()
    notes_model.create_table_parts()
    hadith_model.create_table()
    books_model.create_table()
    audio_model.create_table()
    asyncio.run(eitaa_bot.send_message(eitaa_channel_id_test, "بات ری استارت شد"))
