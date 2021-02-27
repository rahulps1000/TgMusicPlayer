from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

import tgmusicplayer.tgcalls
from tgmusicplayer.converter import convert
from tgmusicplayer.youtube import download
import tgmusicplayer.sira
from tgmusicplayer.helpers.wrappers import errors

from selenium import webdriver
import time 
import os
import re

ydl_opts = {}

async def vidstrip(playlist):
    for i in range(len(playlist)):
        end=playlist[i].find("&")
        playlist[i]=playlist[i][:end]
    return playlist


@Client.on_message(
    filters.command("play")
    & filters.group
    & ~ filters.edited
)
@errors
async def play(client: Client, message_: Message):
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
        await message_.reply_text("You did not provide a video URL.")
        return

    url = text[offset:offset+length]

    await message_.reply_text("Downloading and converting...")

    file_path = await convert(download(url))

    if message.chat.id in tgcalls.playing:
        position = await sira.add(message.chat.id, file_path)
        await message_.reply_text(f"Queued at position {position}.")
    else:
        await message_.reply_text("Playing...")
        tgcalls.pytgcalls.join_group_call(message_.chat.id, file_path, 48000)


@Client.on_message(
    filters.command("playlist")
    & filters.group
    & ~ filters.edited
)
@errors
async def playlist(client: Client, message_: Message):
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
        await message_.reply_text("You did not provide a video URL.")
        return

    url = text[offset:offset+length]

    await message_.reply_text("Downloading and converting...")

    driver = webdriver.Chrome()
	driver.get(url)
	time.sleep(5)
	playlist=[]
	videos=driver.find_elements_by_class_name('style-scope ytd-playlist-video-renderer')
	for video in videos:
	    link=video.find_element_by_xpath('.//*[@id="thumbnail"]/a').get_attribute("href")
	    playlist.append(link)
	driver.quit()

	for urls in vidstrip(playlist):
	    file_path = await convert(download(urls))

	    if message.chat.id in tgcalls.playing:
	        position = await sira.add(message.chat.id, file_path)
	        await message_.reply_text(f"Queued at position {position}.")
	    else:
	        await message_.reply_text("Playing...")
	        tgcalls.pytgcalls.join_group_call(message_.chat.id, file_path, 48000)