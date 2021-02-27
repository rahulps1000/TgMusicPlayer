from pyrogram import Client as Bot

from tgmusicplayer.tgcalls import run
from tgmusicplayer.config import API_ID, API_HASH, BOT_TOKEN


bot = Bot(
    ":memory:",
    API_ID,
    API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="tgmusicplayer/handlers")
)

bot.start()
run()
