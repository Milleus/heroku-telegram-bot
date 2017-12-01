# -*- coding: utf-8 -*-
"""Telegram bot"""
import os
import urllib

import cloudinary
import cloudinary.api
import cloudinary.uploader
import cloudinary.utils
import telebot

CONST_TEMP_IMAGE_FILE_NAME = "temp.jpg"

TOKEN = os.environ['TELEGRAM_TOKEN']
BOT = telebot.TeleBot(TOKEN)
TEST_ID = int(0)
cloudinary.config(
    cloud_name="eu-sep",
    api_key="511481921314569",
    api_secret="ERbXpHjdMlU91qcBEslQCY5ReyE"
)
USER_IMAGE_DICTIONARY = {}


def upload(url):
    """Uploads user-uploaded image onto Cloudinary"""
    cloudinary.uploader.upload(
        url,
        use_filename=True,
        unique_filename=True)


def downloadimagefile(url):
    """Download image from URL and save into temp file"""
    f = open(CONST_TEMP_IMAGE_FILE_NAME, 'wb')
    f.write(urllib.request.urlopen(url).read())
    f.close()


@BOT.message_handler(content_types=['photo'])
def user_uploads_photo(photo):
    """When user uploads an image"""
    filename = BOT.get_file(photo.photo[-1].file_id).file_path
    url = "https://api.telegram.org/file/bot" + TOKEN + "/" + filename
    username = photo.from_user.username

    if username not in USER_IMAGE_DICTIONARY:
        BOT.reply_to(photo, "Use /create_test so that we know these images belong to you")
    else:
        USER_IMAGE_DICTIONARY[photo.from_user.username].append(url)
        print(USER_IMAGE_DICTIONARY)


@BOT.message_handler(content_types=['document'])
def user_uploads_document(message):
    """When user uses the wrong upload button"""
    BOT.reply_to(
        message, "Please use the attach image button instead of attaching a document")


@BOT.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Default command"""
    BOT.reply_to(message, "Use /create_test to start")


@BOT.message_handler(commands=['create_test'])
def create_test(message):
    """Initialize the hashmap where username is key"""
    USER_IMAGE_DICTIONARY[message.chat.username] = [0]
    BOT.reply_to(message, "Proceed to upload your images, " +
                 "and call /start_test in your target chat group after you are done")


@BOT.message_handler(commands=['start_test'])
def start_test(message):
    """Retrieve images from hashmap and display as images"""
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
    username = message.chat.username

    for idx, url in enumerate(USER_IMAGE_DICTIONARY[username]):
        if idx == 0:
            continue
        downloadimagefile(url)
        photo = open(CONST_TEMP_IMAGE_FILE_NAME, 'rb')
        BOT.send_photo(message.chat.id, photo, '/Option' + str(idx))
        option_btn = telebot.types.KeyboardButton("Option " + str(idx))
        markup.add(option_btn)

    BOT.send_message(message.chat.id, "Which is the best?", reply_markup=markup)


@BOT.message_handler(regexp=r'(option|Option).*')
def retrieve_response(message):
    print(message)

BOT.polling()
