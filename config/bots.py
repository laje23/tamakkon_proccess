import os
from balethon import Client
from app_manager import EitaaBot

bale_bot = Client(os.getenv("BALE_BOT_TOKEN"), time_out=60.0)
eitaa_bot = EitaaBot(os.getenv("EITAA_BOT_TOKEN"))
