###                OURFINALS TELEGRAM BOT                ###
### AUTHORED BY ADITYA BANERJEE AND ANSEL CHEUNG HENG YU ###
###               V1.0.0 (DEV) - 2 MAY 2022              ###

### dependencies
import os
import telebot

from flask import Flask, request
from decouple import config

### config variables
port = int(os.environ.get('PORT', '8080'))
bot_apiKey = config('of_apiKey')
bot = telebot.TeleBot(bot_apiKey)
server = Flask(__name__)

### global variables
types = telebot.types
forceReply = types.ForceReply(selective=False)

### message handlers
@bot.message_handler(commands=['start'])
def startHandler(message):
    username = message.chat.username
    reply = f"Hello {username}! This bot is still a work in progress, so please try again later."
    bot.send_message(message.chat.id, reply)

### polling
if __name__ == "__main__":
    bot.polling()