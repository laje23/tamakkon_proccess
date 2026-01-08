from utils.keyboard import *


class UserService:
    def __init__(self, user_model, bale_bot):
        self.model = user_model
        self.bot = bale_bot

    async def handel_login_button(self, author, message_id):
        await self.bot.edit_message_text(
            author.id,
            message_id,
            "خوش آمدید لطفا نام خود را وارد کنید",
            back_to_main_menu(),
        )
        author.set_state("LOGIN")

    async def insert_user(self, author, name):
        self.model.add_user(author.id, name)
        await self.bot.send_message(
            author.id, " تبریک میگم شما وارد شدید.", main_menu(author.id)
        )
