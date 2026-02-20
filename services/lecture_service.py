# services/lecture_service.py

from services.base_service import BaseService
from utils.response import success_response 
from utils.media import file_id_to_bynery
from models.media_model import MediaTableManager 
from models.lecture_model import LectureTableManager


class LectureService(BaseService):
    def __init__(self, bale_bot, eitaa_bot):
        """
        سرویس مدیریت ارسال سخنرانی‌ها
        """
        super().__init__(db_model='', bale_bot=bale_bot, eitaa_bot=eitaa_bot)
        
    def save_lecture(self ,message):
        if lectur_id := message.document.id:
            
            with MediaTableManager() as db:
                media_id = db.insert(lectur_id , 'audio')
            if not media_id :
                return
            with LectureTableManager() as db :
                db.insert(media_id=media_id , caption=str(message.caption))
            
            

    async def auto_send(self):
        with LectureTableManager() as db :
            audio = db.get_one_unsent()
            if not audio:
                return success_response('پیامی برای ارسال وجود ندارد')
            id, caption, sent, file_id = audio
            caption = (caption or "") + "\n\n#سخنرانی\n@tamakkon_ir"
            bin_file = await file_id_to_bynery(file_id=file_id , bot =self.bale_bot)
            try :
                await self.send_media('audio' , bin_file=bin_file , caption=caption )
                db.mark_as_sent(id)
            except :
                return 'خطا در ازسال سخنرانی'
            return success_response('ارسال سخنرانی انجام شد ')