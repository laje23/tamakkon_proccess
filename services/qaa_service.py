from utils.keyboard import *
from balethon.objects import InlineKeyboard, InlineKeyboardButton
import random


class QAAService:
    def __init__(self, bale_bot, qaa_collection, qaa_question, user_model):
        self.bot = bale_bot
        self.user_temp_data = {}
        self.model_collection = qaa_collection
        self.model_question = qaa_question
        self.model_user = user_model

    # save_qaa

    async def save_qaa_title(self, author, text):
        self.user_temp_data[author.id] = {}
        if self.model_collection.collection_exists(text):
            await self.bot.send_message(
                author.id, "شما آن را دارید\nلطفا عنوانی جدید وارد کنید", back_menu()
            )
            return

        else:
            collection_id = self.model_collection.add_collection(text)
            await self.bot.send_message(author.id, "با موفقیت ذخیره شد", back_menu())
            return

    async def save_qaa_state_1(self, author, id):
        self.user_temp_data[author.id] = {"collection_id": id}
        await self.bot.send_message(author.id, "متن پرسش رو وارد کن")
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
        self.user_temp_data.pop(author.id, None)
        await self.bot.send_message(
            author.id, "پرسش و پاسخ با موفقیت ثبت شد", back_menu()
        )

    # edit qaa

    async def edit_qaa_tilt_1(self, author, collection_id):
        self.user_temp_data[author.id] = {"collection_id": collection_id}
        await self.bot.send_message(author.id, "متن جدید را وارد کنید", back_menu())
        author.set_state("EDIT_QAA_TITLE")

    async def edit_qaa_title_2(self, author, text):
        collection_id = self.user_temp_data[author.id]["collection_id"]
        self.model_collection.update_collection_title(collection_id, text)
        await self.bot.send_message(author.id, "با موفقیت تغییر کرد", back_menu())
        self.user_temp_data.pop(author.id, None)
        author.del_state()

    async def edit_qaa_description_1(self, author, collection_id):
        self.user_temp_data[author.id] = {"collection_id": collection_id}
        await self.bot.send_message(author.id, "متن جدید را وارد کنید", back_menu())
        author.set_state("EDIT_QAA_DESCRIPTION")

    async def edit_qaa_description_2(self, author, text):
        collection_id = self.user_temp_data[author.id]["collection_id"]
        self.model_collection.update_collection_description(collection_id, text)
        await self.bot.send_message(author.id, "با موفقیت تغییر کرد", back_menu())
        self.user_temp_data.pop(author.id, None)
        author.del_state()

    # qaa to user

    async def do_qaa_conf(self, author, message_id, collection_id):
        author.set_state("DOING_ANSWERS")
        max_index = self.model_question.get_question_count(collection_id)
        self.user_temp_data[author.id] = {
            "question_index": 1,
            "collection_id": collection_id,
            "max_index": max_index,
        }
        (
            id,
            _,
            _,
            question_text,
            option1,
            option2,
            option3,
            correct,
        ) = self.model_question.get_question(collection_id, 1)
        buttons = []
        for i in (option1, option2, option3):
            button = InlineKeyboardButton(str(i), f"bad")
            buttons.append([button])

        button = InlineKeyboardButton(str(correct), f"good")
        buttons.append([button])

        random.shuffle(buttons)
        await self.bot.edit_message_text(
            author.id, message_id, str(question_text), InlineKeyboard(*buttons)
        )

    async def handel_qaa_answers(self, author, message_id, answer):
        index = self.user_temp_data[author.id]["question_index"]
        self.user_temp_data[author.id][f"answer:{index}"] = answer
        if index < self.user_temp_data[author.id]["max_index"]:
            self.user_temp_data[author.id]["question_index"] = index + 1
            (
                id,
                collection_id,
                question_index,
                question_text,
                option1,
                option2,
                option3,
                correct,
            ) = self.model_question.get_question(collection_id, index + 1)
            buttons = []
            for i in (option1, option2, option3):
                button = InlineKeyboardButton(str(i), f"bad")
                buttons.append([button])

            button = InlineKeyboardButton(str(correct), f"good")
            buttons.append([button])

            random.shuffle(buttons)
            await self.bot.edit_message_text(
                author.id, message_id, str(question_text), InlineKeyboard(*buttons)
            )

        else:
            collection_id = self.user_temp_data[author.id]["collection_id"]
            answers = [
                v
                for k, v in self.user_temp_data[author.id].items()
                if k.startswith("answer")
            ]
            all_good = all(x == "good" for x in answers)
            if all_good:
                self.model_user.add_result(collection_id, author.id, 1)
            else:
                self.model_user.add_result(collection_id, author.id, 0)

            self.user_temp_data.pop(author.id, None)
            await self.bot.edit_message_text(
                author.id,
                message_id,
                "سوالات به پایان رسید ممنون از شرکت شما\nنتیجه به شما اطلاع رسانی میشود",
                InlineKeyboard([InlineKeyboardButton("بازگشت", "back_to_main")]),
            )

    async def start_edit_field(self, author, question_id, field):
        self.user_temp_data[author.id] = {"question_id": question_id, "field": field}

        await self.bot.send_message(
            author.id, f"متن جدید برای «{field}» را وارد کنید:", back_menu()
        )

        author.set_state("EDIT_QAA_FIELD")

    async def commit_edit_field(self, author, new_value):
        temp = self.user_temp_data.get(author.id)
        if not temp:
            return await self.bot.send_message(author.id, "خطا: اطلاعات یافت نشد.")

        qid = temp["question_id"]
        field = temp["field"]

        # مپ کردن فیلدها به توابع مدل
        updater = {
            "text": self.model_question.update_question_text,
            "option1": self.model_question.update_option1,
            "option2": self.model_question.update_option2,
            "option3": self.model_question.update_option3,
            "correct": self.model_question.update_correct,
        }

        update_func = updater.get(field)
        if update_func:
            update_func(qid, new_value)

        await self.bot.send_message(author.id, "با موفقیت تغییر کرد ✔️", back_menu())

        # پاکسازی
        self.user_temp_data.pop(author.id, None)
        author.del_state()
