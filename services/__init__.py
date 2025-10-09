from config.bots import bale_bot , eitaa_bot
from config.setting import user_temp_data
from ..services.book_sarvice import BookService 
from ..services.hadith_service import HadithService
from ..services.note_service import NoteService
from ..services.clip_service import ClipService
from ..services.general_service import GeneralService
from ..services.lecture_service import LectureService



book_services = BookService(bale_bot , eitaa_bot)
hadith_services = HadithService(bale_bot , eitaa_bot)
note_services =NoteService(user_temp_data ,bale_bot , eitaa_bot)
clip_services =ClipService(bale_bot , eitaa_bot)
lecture_services = LectureService(bale_bot , eitaa_bot)
general_services = GeneralService(user_temp_data ,bale_bot , eitaa_bot)