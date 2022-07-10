###                OURFINALS TELEGRAM BOT                ###
### AUTHORED BY ADITYA BANERJEE AND ANSEL CHEUNG HENG YU ###
###              V1.0.1 (TEST) - 2 MAY 2022              ###

### dependencies
import os
import telebot
import requests

from flask import Flask, request
from decouple import config
from data.data import *

from utils import *

### config variables
port = int(os.environ.get('PORT', '8080'))
bot_apiKey = config('of_apiKey')
bot = telebot.TeleBot(bot_apiKey)
server = Flask(__name__)
apiServerUrl = 'https://ourfinals-telebot-server.herokuapp.com/'
nusModsUrl = 'https://api.nusmods.com/v2/2021-2022/modules/'

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
    headers = {'x-api-key': config('server_apiKey')}
    response = requests.get(f"{apiServerUrl}users/username/{username}", None, headers=headers)
    greeting = ''
    if response.status_code == 404:
        greeting = f"Hello, and welcome to OurFinals! Would you like me to sign you up?"
        keyAugment.add('yes', 'no')
        bot.send_message(id, greeting, reply_markup=keyAugment)
        bot.register_next_step_handler(message, signupStartHandler)
    else:
        greeting = f"Welcome back {username}! How can I help you?"
        keyAugment.add('view profile', 'add an assignment', 'teach an assignment', 'exit')
        bot.send_message(id, greeting, reply_markup=keyAugment)
        bot.register_next_step_handler(message, menuOptionsHandler)

### Menu Handlers
def mainMenu(message):
    keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    username = message.chat.username
    id = message.chat.id
    prompt = f"How can I help you, {username}?"
    keyAugment.add('view profile', 'add an assignment', 'teach an assignment', 'exit')
    bot.send_message(id, prompt, reply_markup=keyAugment)
    bot.register_next_step_handler(message, menuOptionsHandler)

def menuOptionsHandler(message):
    id = message.chat.id
    if message.text == 'view profile':
        viewProfileHandler(message)
    elif message.text == 'add an assignment':
        addAssignmentHandler(message)
    elif message.text == 'teach an assignment':
        teachAssignmentHandler(message)
    elif message.text == 'exit':
        exitHandler(message)
    else:
        reply = "You've selected an invalid option, please try again"
        bot.send_message(id, reply)
        mainMenu(message)

def exitHandler(message):
    id = message.chat.id
    reply = "You can use /start to pull up the main menu again whenever you'd like. See you around!"
    bot.send_message(id, reply)

### Signup Handlers
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
        reply = "What faculty are you in?"
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
            headers = {'x-api-key': config('server_apiKey')}
            response = requests.post(f"{apiServerUrl}users/add", signupData, headers=headers)
            if response.status_code == 200:
                reply = 'Welcome to OurFinals!'
                bot.send_message(id, reply)
                mainMenu(message)
            else:
                reply = 'I was unable to sign you up... Please try again.'
                bot.send_message(id, reply)
                message.text = 'yes'
                signupStartHandler(message)
        except:
            reply = 'I was unable to sign you up... Please try again.'
            bot.send_message(id, reply)
            message.text = 'yes'
            signupStartHandler(message)
    else:
        reply = 'You have entered an invalid NUSNET ID! Please try again.'
        bot.send_message(id, reply)
        bot.register_next_step_handler(message, signupCompleteHandler, signupData)

### Functional Handlers - View Profile
def viewProfileHandler(message):
    username = message.chat.username
    id = message.chat.id
    headers = {'x-api-key': config('server_apiKey')}
    response = requests.get(f"{apiServerUrl}users/username/{username}", None, headers=headers)
    reply = formatUserData(response)
    bot.send_message(id, reply)
    mainMenu(message)

### Functional Handlers - Add Assignment
def addAssignmentHandler(message):
    id = message.chat.id
    reply = "Are you sure you want to add a new assignment?"
    keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    keyAugment.add('yes', 'no')
    bot.send_message(id, reply, reply_markup=keyAugment)
    bot.register_next_step_handler(message, addAssignmentStartHandler)

def addAssignmentStartHandler(message):
    id = message.chat.id
    username = message.chat.username
    headers = {'x-api-key': config('server_apiKey')}
    response = requests.get(f"{apiServerUrl}users/username/{username}", None, headers=headers)
    student = response.json()
    assignmentData = {
        "faculty": student["faculty"]
    }
    if message.text == 'yes':
        reply = "Enter the module code for the assignment."
        bot.send_message(id, reply, reply_markup=forceReply)
        bot.register_next_step_handler(message, moduleCodeHandler, assignmentData)
    elif message.text == 'no':
        mainMenu(message)
    else:
        reply = "I didn't catch that."
        bot.send_message(id, reply)
        mainMenu(message)

def moduleCodeHandler(message, assignmentData):
    # make an API call to NUSMods to see if a valid module code was entered
    id = message.chat.id
    test_module_code = message.text.upper()
    response = requests.get(f"{nusModsUrl}{test_module_code}.json")
    if response.status_code == 404:
        reply = 'You have entered an invalid module code, please try again.'
        bot.send_message(id, reply, reply_markup=forceReply)
        invalidModuleCodeHandler(message, assignmentData)
    else :
        assignmentData['module_code'] = test_module_code
        reply = "Enter the title for the assignment."
        bot.send_message(id, reply)
        bot.register_next_step_handler(message, titleHandler, assignmentData)

def invalidModuleCodeHandler(message, assignmentData):
    id = message.chat.id
    reply = "Enter the module code for the assignment."
    bot.send_message(id, reply, reply_markup=forceReply)
    bot.register_next_step_handler(message, moduleCodeHandler, assignmentData)

def titleHandler(message, assignmentData):
    id = message.chat.id
    test_title = message.text
    if test_title == '':
        reply = "You've entered an invalid title, please try again."
        bot.send_message(id, reply, reply_markup=forceReply)
        invalidTitleHandler(message, assignmentData)
    else:
        assignmentData['title'] = test_title
        reply = "Enter a description for the assignment."
        bot.send_message(id, reply)
        bot.register_next_step_handler(message, descriptionHandler, assignmentData)

def invalidTitleHandler(message, assignmentData):
    id = message.chat.id
    reply = "Enter the title for the assignment."
    bot.send_message(id, reply, reply_markup=forceReply)
    bot.register_next_step_handler(message, titleHandler, assignmentData)

def descriptionHandler(message, assignmentData):
    id = message.chat.id
    test_description = message.text
    if test_description == '':
        reply = "You've entered an invalid description, please try again."
        bot.send_message(id, reply, reply_markup=forceReply)
        invalidDescriptionHandler(message, assignmentData)
    else:
        assignmentData['description'] = test_description
        reply = "Add a link to a supporting to document for the assignment. Make sure link-sharing is enabled."
        bot.send_message(id, reply)
        bot.register_next_step_handler(message, fileHandler, assignmentData)

def invalidDescriptionHandler(message, assignmentData):
    id = message.chat.id
    reply = "Enter a description for the assignment."
    bot.send_message(id, reply, reply_markup=forceReply)
    bot.register_next_step_handler(message, descriptionHandler, assignmentData)

def fileHandler(message, assignmentData):
    id = message.chat.id
    test_file_link = message.text
    if test_file_link == '':
        reply = "You've entered an invalid file link, please try again."
        bot.send_message(id, reply, reply_markup=forceReply)
        invalidFileHandler(message, assignmentData)
    else:
        assignmentData['file_link'] = test_file_link
        addAssignmentCompleteHandler(message, assignmentData)

def invalidFileHandler(message, assignmentData):
    id = message.chat.id
    reply = "Add a link to a supporting to document for the assignment. Make sure link-sharing is enabled."
    bot.send_message(id, reply, reply_markup=forceReply)
    bot.register_next_step_handler(message, fileHandler, assignmentData)

def addAssignmentCompleteHandler(message, assignmentData):
    id = message.chat.id
    username = message.chat.username
    assignmentData['student_username'] = username
    assignmentData['tutor_username'] = ''
    headers = {'x-api-key': config('server_apiKey')}
    assignment_res = requests.post(f"{apiServerUrl}assignments/add", assignmentData, headers=headers)
    assignment_id = assignment_res.json()["_id"]
    user_res = addAssignmentToUser(username, assignment_res.json()['_id'], headers);
    if assignment_res.status_code == 200 and user_res.status_code == 200:
        reply = "You're all set! Potential tutors will see your assignment shortly."
        bot.send_message(id, reply)
        notifyPotentialTutors(message, assignmentData);
    else:
        reply = 'We were unable to add your assignment, please try again later.'
        bot.send_message(id, reply)
    mainMenu(message)
    
def notifyPotentialTutors(message, assignmentData):
    faculty = assignmentData["faculty"]
    username = message.chat.username
    headers = {'x-api-key': config('server_apiKey')}
    response = requests.get(f"{apiServerUrl}users/faculty/{faculty}", None, headers=headers)
    users = list(response.json())
    for user in users:
        if not user["username"] == username:
            id = user["chat_id"]
            reply = f"A student from your faculty added an assignment!"
            bot.send_message(id, reply)

def addAssignmentToUser(username, assignment_id, headers):
    response = requests.post(f"{apiServerUrl}users/{username}/assignments_as_student/add", {
        '_id': assignment_id
    }, headers=headers)
    return response

### Functional Handlers - Teach Assignment
def teachAssignmentHandler(message):
    id = message.chat.id
    reply = "Are you sure you want to teach an assignment?"
    keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    keyAugment.add('yes', 'no')
    bot.send_message(id, reply, reply_markup=keyAugment)
    bot.register_next_step_handler(message, teachAssignmentTypeHandler)

def teachAssignmentTypeHandler(message):
    id = message.chat.id
    reply = 'You can either view assignments posted by other students from your faculty, or search for assignments by module code. What would you like to do?'
    keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    keyAugment.add('View assignments from my faculty', 'Search assignments by module code')
    bot.send_message(id, reply, reply_markup=keyAugment)
    bot.register_next_step_handler(message, teachAssignmentStartHandler)

def teachAssignmentStartHandler(message):
    id = message.chat.id
    if message.text == 'Search assignments by module code':
        reply = "Which module would you like to view assignments from? Please enter a module code."
        bot.send_message(id, reply, reply_markup=forceReply)
        bot.register_next_step_handler(message, fetchAssignments, "module")
    elif message.text == 'View assignments from my faculty':
        fetchAssignments(message, "faculty")
    else:
        reply = 'You have selected an invalid option, please try again.'
        bot.send_message(id, reply)
        mainMenu(message)

@bot.message_handler(commands=['view'])
def viewAssignmentsCommandHandler(message):
    fetchAssignments(message, "faculty")

def fetchAssignments(message, type, assignments=None, initial=True, repeat_code=None):
    id = message.chat.id
    username = message.chat.username
    if type == "module":
        if initial:
            code = str(message.text).upper()
            headers = {'x-api-key': config('server_apiKey')}
            response = requests.get(f"{apiServerUrl}assignments/code/{code}", headers=headers)
            assignments = list(response.json())
        else:
            code = repeat_code
    else: 
        headers = {'x-api-key': config('server_apiKey')}
        student_response = requests.get(f"{apiServerUrl}users/username/{username}", headers=headers)
        faculty = student_response.json()["faculty"]
        assignment_response = requests.get(f"{apiServerUrl}assignments/faculty/{faculty}", headers=headers)
        assignments = list(assignment_response.json())
    current_assignments = assignments
    if len(assignments) == 0:
        if type == "module":
            reply = f"There are no assignments from {code} right now, please try again later."
        else:
            reply = f"There are no assignments posted by members of your faculty right now, please try again later."
        bot.send_message(id, reply)
        mainMenu(message)
    else:
        keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyAugment.add('teach one of these assignments')
        if len(assignments) > 5:
            keyAugment.add('view more assignments')
            current_assignments = assignments[:5]
            assignments = assignments[5:]
        keyAugment.add('exit')
        if type == "module":
            reply = f"Here are some assignments from {code}:"
        else:
            reply = "Here are some assignments from your faculty:"
        index = 0
        for assignment in current_assignments:
            index+=1
            reply += f"\n\n{index}: {formatAssignmentData(assignment)}"
        reply += f"\n\nWhat would you like to do?"
        bot.send_message(id, reply, reply_markup=keyAugment)
        if type == "module":
            bot.register_next_step_handler(message, fetchAssignmentsLoopHandler, type, current_assignments, assignments, code)
        else:
            bot.register_next_step_handler(message, fetchAssignmentsLoopHandler, type, current_assignments, assignments)

def fetchAssignmentsLoopHandler(message, type, current_assignments, assignments, code=None):
    id = message.chat.id
    option = message.text
    if option == 'teach one of these assignments':
        selectAssignment(message, current_assignments)
    elif option == 'view more assignments':
        fetchAssignments(message, type, assignments, False, code)
    elif option == 'exit':
        reply = 'See you around!'
        bot.send_message(id, reply)
        mainMenu(message)
    else:
        reply = 'You have chosen an invalid option, please try again.'
        bot.send_message(id, reply)
        mainMenu(message)

def selectAssignment(message, assignments):
    id = message.chat.id
    reply = 'Which assignment would you like to teach?'
    keyAugment = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for i in range(1, len(assignments) + 1):
        keyAugment.add(str(i))
    bot.send_message(id, reply, reply_markup=keyAugment)
    bot.register_next_step_handler(message, validateAssignmentSelection, assignments)

def validateAssignmentSelection(message, assignments):
    id = message.chat.id
    username = message.chat.username
    index = int(message.text)
    if index not in range(1, len(assignments) + 1):
        reply = 'You have entered an invalid selection, please try again.'
        bot.send_message(id, reply)
        mainMenu(message)
    else:
        test_assignment = assignments[index - 1]
        student_username = test_assignment['student_username']
        module_code = test_assignment["module_code"]
        if student_username == username:
            reply = 'You cannot be the tutor for your own assignment, please try again.'
            bot.send_message(id, reply)
            mainMenu(message)
        else:
            assignment_id = test_assignment["_id"]
            headers = {'x-api-key': config('server_apiKey')}
            response = requests.post(f"{apiServerUrl}assignments/id/{assignment_id}/tutor/add", {
                "tutor_username": username
            }, headers=headers)
            tutor_response = requests.post(f"{apiServerUrl}users/{username}/assignments_as_tutor/add", {
                '_id': assignment_id
            }, headers=headers)
            if response.status_code == 200 and tutor_response.status_code == 200:
                reply = f"You have been added as the tutor for @{student_username}'s {module_code} assignment!"
                student_message = f"@{username} has been added as the tutor for your {module_code} assignment!"
                student_response = requests.get(f"{apiServerUrl}users/username/{student_username}", headers=headers)
                student = student_response.json()
                student_chat_id = student['chat_id']
                bot.send_message(id, reply)
                bot.send_message(student_chat_id, student_message)
            else:
                reply = "Sorry, something went wrong. Please try again later."
                bot.send_message(id, reply)
                mainMenu(message)

@server.route('/' + bot_apiKey, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200

@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://ourfinals-telebot.herokuapp.com/' + bot_apiKey)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
