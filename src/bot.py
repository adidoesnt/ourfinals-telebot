###                OURFINALS TELEGRAM BOT                ###
### AUTHORED BY ADITYA BANERJEE AND ANSEL CHEUNG HENG YU ###
###               V1.0.0 (DEV) - 2 MAY 2022              ###

### dependencies
import os
import telebot
import requests

from flask import Flask
from decouple import config
from data.data import *

### config variables
port = int(os.environ.get('PORT', '8080'))
bot_apiKey = config('of_apiKey')
bot = telebot.TeleBot(bot_apiKey)
server = Flask(__name__)
apiServerUrl = 'https://ourfinals-telebot-server.herokuapp.com/'

### global variables
types = telebot.types
forceReply = types.ForceReply(selective=False)

### message handlers
@bot.message_handler(commands=['start'])
def startHandler(message):
    keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    username = message.chat.username
    id = message.chat.id
    response = requests.get(f"{apiServerUrl}users/{username}")
    greeting = ''
    if response.text == '':
        greeting = f"Hello, and welcome to OurFinals! Would you like me to sign you up?"
        keyAugment.add('yes')
        keyAugment.add('no')
        bot.send_message(id, greeting, reply_markup=keyAugment)
        bot.register_next_step_handler(message, signupStartHandler)
    else:
        greeting = f"Welcome back {username}! How can I help you?"
        keyAugment.add('view profile')
        bot.send_message(id, greeting, reply_markup=keyAugment)

def signupStartHandler(message):
    reply = ''
    id = message.chat.id
    if message.text == 'yes':
        keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        reply = "Great! What faculty are you in?"
        for faculty in faculties:
            keyAugment.add(faculty)
        bot.send_message(id, reply, reply_markup=keyAugment)
    else:
        reply = "See you around!"
        bot.send_message(id, reply)    

### polling
if __name__ == "__main__":
    bot.polling()