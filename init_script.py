from models import (
    audios_model,
    books_model,
    clips_model,
    hadith_model,
    lectures_model,
    notes_model,
    permissions_model,
    qaa_collection_model,
    qaa_questions_model,
    qaa_result_model,
    user_model,
    user_permission_model,
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
    user_model.create_table()
    qaa_collection_model.create_collections_table()
    qaa_questions_model.create_questions_table()
    qaa_result_model.create_results_table()
    permissions_model.create_permission_table()
    user_permission_model.create_user_permission_table()
    
    print(permissions_model.insert_default_permissions())
    
    asyncio.run(
        eitaa_bot.send_message(eitaa_channel_id_test, os.getenv("RESTART_MESSAGE"))
    )
