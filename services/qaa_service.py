from utils.keyboard import *


class QAAService:
    def __init__(self, bale_bot, qaa_collection, qaa_question):
        self.bot = bale_bot
        self.user_temp_data = {}
        self.model_collection = qaa_collection
        self.model_question = qaa_question

    async def save_qaa_state_1(self, author, text):
        self.user_temp_data[author.id] = {}
        if x := self.model_collection.collection_exists(text):
            await self.bot.send_message(
                author.id,
                "شما آن را دارید\nاگر مایل به اضافه کردن سوال هستید متن ان را ارسال کنید",
                back_menu(),
            )
            self.user_temp_data[author.id]["collection_id"] = x
            author.set_state("ENTER_QAA_TEXT")

        else:
            collection_id = self.model_collection.add_collection(text)
            self.user_temp_data[author.id]["collection_id"] = collection_id
            await self.bot.send_message(author.id, "لطفا متن پرسش رو بنویسید")
            author.set_state("ENTER_QAA_TEXT")

    async def save_qaa_state_2(self, author, text):
        self.user_temp_data[author.id]["question_text"] = text
        await self.bot.send_message(author.id, "حالا جواب غلط اول رو بفرست")
        author.set_state("ENTER_QAA_QUESTION_1")

    async def save_qaa_state_3(self, author, text):
        self.user_temp_data[author.id]["option_1"] = text
        await self.bot.send_message(author.id, "حالا جواب غلط دوم رو بفرست")
        author.set_state("ENTER_QAA_QUESTION_2")

    async def save_qaa_state_4(self, author, text):
        self.user_temp_data[author.id]["option_2"] = text
        await self.bot.send_message(author.id, "حالا جواب غلط سوم رو بفرست")
        author.set_state("ENTER_QAA_QUESTION_3")

    async def save_qaa_state_5(self, author, text):
        self.user_temp_data[author.id]["option_3"] = text
        await self.bot.send_message(author.id, "حالا جواب درست رو بفرست")
        author.set_state("ENTER_QAA_CORRECT_OPTION")

    async def save_qaa_state_6(self, author, text):
        collection_id = self.user_temp_data[author.id]["collection_id"]
        question_text = self.user_temp_data[author.id]["question_text"]
        option_1 = self.user_temp_data[author.id]["option_1"]
        option_2 = self.user_temp_data[author.id]["option_2"]
        option_3 = self.user_temp_data[author.id]["option_3"]
        correct_option = text

        self.model_question.add_question(
            collection_id, question_text, option_1, option_2, option_3, correct_option
        )

        author.del_state()
        await self.bot.send_message(
            author.id, "پرسش و پاسخ با موفقیت ثبت شد", back_menu()
        )
