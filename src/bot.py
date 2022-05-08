###                OURFINALS TELEGRAM BOT                ###
### AUTHORED BY ADITYA BANERJEE AND ANSEL CHEUNG HENG YU ###
###               V1.0.0 (DEV) - 2 MAY 2022              ###

### dependencies
import os
from urllib import response
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
removeMarkup = types.ReplyKeyboardRemove(selective=False)

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

def mainMenu(message):
    username = message.chat.username
    id = message.chat.id
    prompt = f"How can I help you, {username}?"
    bot.send_message(id, prompt)

def signupStartHandler(message):
    id = message.chat.id
    signupData = {
        'username': message.chat.username,
        'chat_id': id,
        "assignments_as_student": [],
        "assignments_as_tutor": []
    }
    reply = ''
    if message.text == 'yes':
        keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        reply = "Great! What faculty are you in?"
        for faculty in faculties:
            keyAugment.add(faculty)
        bot.send_message(id, reply, reply_markup=keyAugment)
        bot.register_next_step_handler(message, facultyHandler, signupData)
    else:
        reply = "See you around!"
        bot.send_message(id, reply)

def facultyHandler(message, signupData):
    testFaculty = str(message.text).lower()
    id = message.chat.id
    if testFaculty in faculties:
        signupData['faculty'] = testFaculty 
        keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for year in range(1, 6):
            keyAugment.add(str(year))
        reply = 'Got it! What year are you in?'
        bot.send_message(id, reply, reply_markup=keyAugment)
        bot.register_next_step_handler(message, yearHandler, signupData)
    else:
        reply = 'You have entered an invalid faculty! Please try again.'
        keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for faculty in faculties:
            keyAugment.add(faculty)
        bot.send_message(id, reply, reply_markup=keyAugment)
        bot.register_next_step_handler(message, facultyHandler, signupData)

def yearHandler(message, signupData):
    id = message.chat.id
    testYear = str(message.text)
    years = ['1', '2', '3', '4', '5']
    if testYear in years:
        signupData['year'] = testYear
        reply = "What's your NUSNET ID? This is the ID that begins with 'E', followed by 7 digits."
        bot.send_message(id, reply)
        bot.register_next_step_handler(message, signupCompleteHandler, signupData)
    else:
        reply = 'You have entered an invalid year! Please try again.'
        keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for year in range(1, 6):
            keyAugment.add(str(year))
        bot.send_message(id, reply, reply_markup=keyAugment)
        bot.register_next_step_handler(message, yearHandler, signupData)

def signupCompleteHandler(message, signupData):
    testId = str(message.text).lower()
    id = message.chat.id
    reply = ''
    if testId.startswith('e') and len(testId) == 8 and testId[1:7].isnumeric():
        signupData['nusnet_id'] = testId
        try:
            response = requests.post(f"{apiServerUrl}users/add", signupData)
            if response.status_code == 200:
                reply = 'Welcome to OurFinals!'
                bot.send_message(id, reply)
                mainMenu(message)
            else:
                reply = 'I was unable to sign you up... Please try again.'
                bot.send_message(id, reply)
                signupStartHandler(message)
        except:
            reply = 'I was unable to sign you up... Please try again.'
            bot.send_message(id, reply)
            signupStartHandler(message)
    else:
        reply = 'You have entered an invalid NUSNET ID! Please try again.'
        bot.send_message(id, reply)
        bot.register_next_step_handler(message, signupCompleteHandler, signupData)

### polling
if __name__ == "__main__":
    bot.polling()