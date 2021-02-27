from pyrogram import filters
from tgmusicplayer.config import SUDO_USERS

sudoers = filters.user(SUDO_USERS)
