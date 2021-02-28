from base64 import urlsafe_b64encode
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.pytgcalls.methods.stream import is_playing

import tgmusicplayer.tgcalls
from tgmusicplayer.converter import convert
from tgmusicplayer.youtube import download
import tgmusicplayer.sira
from tgmusicplayer.config import DURATION_LIMIT
from tgmusicplayer.helpers.wrappers import errors
from tgmusicplayer.helpers.errors import DurationLimitError

from selenium import webdriver
import time
import os

ydl_opts = {} 

def vidstrip(playlist):
    for i in range(len(playlist)):
        end=playlist[i].find("&")
        playlist[i]=playlist[i][:end]
    return playlist

@Client.on_message(
    filters.command("playlist")
    & filters.group
    & ~ filters.edited
)
@errors
async def play(client: Client, message_: Message):
    audio = (message_.reply_to_message.audio or message_.reply_to_message.voice) if message_.reply_to_message else None

    res = await message_.reply_text("🔄 Processing...")

    if audio:
        if round(audio.duration / 60) > DURATION_LIMIT:
            raise DurationLimitError(
                f"Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {audio.duration / 60} minute(s)"
            )

        file_name = audio.file_id + audio.file_name.split(".")[-1]
        file_path = await convert(await message_.reply_to_message.download(file_name))
    else:
        messages = [message_]
        text = ""
        offset = None
        length = None

        if message_.reply_to_message:
            messages.append(message_.reply_to_message)

        for message in messages:
            if offset:
                break

            if message.entities:
                for entity in message.entities:
                    if entity.type == "url":
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break

        if offset == None:
            await res.edit_text("❕ You did not give me anything to play.")
            return

        urls = text[offset:offset+length]

        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        driver.get(urls)
        time.sleep(5)
        playlist=[]
        videos=driver.find_elements_by_class_name('style-scope ytd-playlist-video-renderer')
        for video in videos:
            link=video.find_element_by_xpath('.//*[@id="thumbnail"]/a').get_attribute("href")
            playlist.append(link)
        driver.quit()
        links = vidstrip(playlist)

        for url in links:
            file_path = await convert(download(url))

            try:
                is_playing = tgcalls.pytgcalls.is_playing(message_.chat.id)
            except:
                is_playing = False

            if is_playing:
                position = await sira.add(message_.chat.id, file_path)
                await res.edit_text(f"#️⃣ Queued at position {position}.")
            else:
                await res.edit_text("▶️ Playing...")
                tgcalls.pytgcalls.join_group_call(message_.chat.id, file_path, 48000)
