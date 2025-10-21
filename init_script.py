from models import (
    audios_model,
    books_model,
    clips_model,
    hadith_model,
    lectures_model,
    notes_model,
)
from config.channels import eitaa_channel_id_test
import os
from config.bots import eitaa_bot
import asyncio


if __name__ == "__main__":
    lectures_model.create_table()
    clips_model.create_table()
    notes_model.create_table()
    notes_model.create_table_parts()
    hadith_model.create_table()
    books_model.create_table()
    audios_model.create_table()
    asyncio.run(
        eitaa_bot.send_message(eitaa_channel_id_test, os.getenv("RESTART_MESSAGE"))
    )
