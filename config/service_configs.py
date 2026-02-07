from config.bots import bale_bot, eitaa_bot
from config.setting import user_temp_data
from services.book_service import BookService
from services.hadith_service import HadithService
from services.note_service import NoteService
from services.clip_service import ClipService
from services.general_service import GeneralService
from services.lecture_service import LectureService
from services.qaa_service import QAAService
from services.user_service import UserService
from models import (
    permissions_model,
    qaa_collection_model,
    qaa_questions_model,
    qaa_result_model,
    user_model,
    user_permission_model
)

book_services = BookService(user_temp_data, bale_bot, eitaa_bot)
hadith_services = HadithService(bale_bot, eitaa_bot)
note_services = NoteService(user_temp_data, bale_bot, eitaa_bot)
clip_services = ClipService(user_temp_data, bale_bot, eitaa_bot)
lecture_services = LectureService(bale_bot, eitaa_bot)
general_services = GeneralService(user_temp_data, bale_bot, eitaa_bot)
qaa_service = QAAService(
    bale_bot, qaa_collection_model, qaa_questions_model, qaa_result_model
)
user_service = UserService(user_model=user_model , bale_bot=bale_bot ,permission_model= permissions_model , user_permission_model= user_permission_model )

__all__ = [
    "book_services",
    "hadith_services",
    "note_services",
    "clip_services",
    "lecture_services",
    "general_services",
    "qaa_service",
    "user_service",
]
