from models import audio, lecture, clips, hadith, notes, books
from config import eitaa_bot, eitaa_channel_id_test
import asyncio


if __name__ == "__main__":
    lecture.create_table()
    clips.create_table()
    notes.create_table()
    notes.create_table_parts()
    hadith.create_table()
    books.create_table()
    audio.create_table()
    asyncio.run(eitaa_bot.send_message(eitaa_channel_id_test, "بات ری استارت شد"))
