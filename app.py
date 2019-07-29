from flask import Flask, request
import requests
from datetime import *
import time
import calendar
from Menu import *
from Calendar import *
import json
import pyrebase
import pytz
import re

app = Flask(__name__)


FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'letthebasseriansyeet'
PAGE_ACCESS_TOKEN = 'EAAidPSNIxU0BAAvOOuFF9VZAoQWqENQLMxGPC36A67YXcJfCZCVKNeUpZAkXboUwTOE61RwkzNbO3kQNtjlZAFhOtZBUt9zbKskKjCdh01Lk6fD0dwLXY7N6c8LxVR76QXFlf0RM6SFYAdflKZC1fYpgJonPziIJlmstlIw2wYbAZDZD'

TIMEZONE = pytz.timezone('Australia/Sydney')

firebaseConfig = {
    "apiKey": "AIzaSyC0DefUGYgP46MIo23Sw_-ODc04h5-AJSU",
    "authDomain": "bssrbot.firebaseapp.com",
    "databaseURL": "https://bssrbot.firebaseio.com",
    "projectId": "bssrbot",
    "storageBucket": "bssrbot.appspot.com",
    "messagingSenderId": "598501915047",
    "appId": "1:598501915047:web:d21aee9382cd478a"
}


firebase = pyrebase.initialize_app(firebaseConfig)
db = firebase.database()

def get_bot_response(message):
    message = message.lower()
    response = []
    gif = None

    if checkIfGreeting(message) or message == "hi" or message == "hey":
        response.append("Hello! Welcome to the Basser Bot! I'm here to help you with all your dino and calendar needs.")
        response.append(f"Here are some example questions:\n1. What's for dino? \n2. What's for lunch today? \n3. What's the calendar for this week? \n4. What's happening on Thursday? \n5. Is shopen?")
        gif = "hello"
    elif message == "thx" or message == "thanks" or message == "thank you":
        response.append("You're welcome!")
        gif = "you're welcome"
    if not response:
        response, gif = checkForDino(message)
        if response:
            response = []
            response.append("Dino hasn't sent through the menu this week :(")
    if not response:
        response, gif = checkForCalendar(message)
    if not response:
        response, gif = checkForShopenLog(message)
    if not response:
        response, gif = checkForEasterEggs(message)
    if not response:
        response.append("Sorry I don't understand, send 'help' for options")

    return response, gif

def checkIfGreeting(message):
    possibleGreetings = ["hello", "hi ", "help", "hey "]
    for el in possibleGreetings:
        if el in message:
            return True        
    return False


def checkForDino(message):
    response = []
    current_day = datetime.now(TIMEZONE).weekday()
    
    time = datetime.now(TIMEZONE).time().hour
    day = "today"
    if "tomorrow" in message:
        day = "tomorrow"
        current_day+=1
        time = 0
        if current_day==7:
            return "Sorry, do not have the menu for next week yet!", "sorry"
    todayMenu = getDayMenu(current_day)
    gif = None
    if "dino" in message or "cooking good looking" in message:
        if time < 10:
            response.append(f"For breakfast {day} is:")
            response.append(todayMenu.breakfast)
        if time < 14:
            response.append(f"For lunch {day} is:")
            response.append(str(todayMenu.lunch))
        if time < 19:
            response.append(f"For dinner {day} is:")
            response.append(str(todayMenu.dinner))
        if not response: 
            response.append("No more meals today :)")
        gif = "dog animals eating dinner"
    elif "breakfast" in message:
        response.append(f"For breakfast {day} is:")
        response.append(todayMenu.breakfast)
        gif = "breakfast"
    elif "lunch" in message:
        response.append(f"For lunch {day} is:")
        response.append(str(todayMenu.lunch))
        if "GET KEEN IT'S SANDWICH DAY 🥪🥪" in response:
            gif = "sandwich"
        else:
            gif = todayMenu.lunch.main
    elif "dinner" in message:
        response.append(f"For dinner {day} is:")
        response.append(str(todayMenu.dinner))
        if f"It's a surprise! It's the chef's choice {day} 👩‍🍳" in response:
            gif = "chef"
        elif "Burger night baby 🍔" in response:
            gif = "burger"
        elif "It's pizza and pasta night 🍕!!" in response:
            gif = "pizza"
        else:
            gif = todayMenu.dinner.main

    return response, gif


def checkForCalendar(message):
    daysOfWeek = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    response = []
    weekNum = calculateWeekNum()
    weekCalendar = getWeek(weekNum)
    gif = None

    if "calendar" in message or "this week" in message:
        response.append(str(weekCalendar))
    if "on today" in message:
        current_day = datetime.now(TIMEZONE).weekday()
        dayName = calendar.day_name[current_day].lower()
        response.append(getattr(weekCalendar, dayName))
        if current_day == 0:
            gif = "monday"
        elif current_day == 4:
            gif = "friday"        
    if "on tomorrow" in message:        
        tomorrow = (datetime.now(TIMEZONE).weekday() + 1)
        if tomorrow == 7:
            tomorrow = 0
        dayName = calendar.day_name[tomorrow].lower()
        response.append(getattr(weekCalendar, dayName))
        if tomorrow == 0:
            gif = "monday"
        elif tomorrow == 4:
            gif = "friday"   
    if "what week" in message:
        response.append(f'It is week {weekNum}')
    for i, day in enumerate(daysOfWeek):
        if day in message:
            response.append(f"This is what's on {day.capitalize()}:")
            dayName = calendar.day_name[i].lower()
            response.append(getattr(weekCalendar, dayName))
    if 'Family Dinner' in response:
        gif = 'family dinner'
    elif 'Coffee Night ☕🖊️' in response:
        gif = 'coffee'
    return response, gif

def checkForShopenLog(message):
    response = []
    gif = None
    if "good evening, i shall be commencing the opening of shopen today" in message:
        #log that shopen in now open 

        name = re.search("[^ -][^-]*$", message)
        #incorrectly input name
        if name.start(0) < 10:
            response.append("Unsuccessfull activation of Shopen, Please enter name after a - or ask Batsey")
            gif = "wtf"
            return response, gif 

        data = {"OpenTimeInSec": datetime.now().timestamp(),
        "OpenTime":datetime.now(TIMEZONE).strftime("%I:%M:%S %p"),
        "Name": name.group(0)}

        db.child("Shopen").update(data)
        response.append("Successfully activated Shopen! Shopen will close automatically in 3 hrs")
        gif = "Yay!"
    elif "good evening, i shall now be closing el shopen" in message:
        #create authentication so only person who opened shop can close it
        pass
    elif "shopen" in message:
        #access firebase to see if shopen is open!
        shopenData = db.child("Shopen").get()
        if shopenData.val() is not None:
            timeInSecs = shopenData.val()["OpenTimeInSec"]
            
            #shop has already been open for 3 hrs autoclose it
            if (datetime.now().timestamp() - timeInSecs) > 7200:
                db.child("Shopen").remove()
                response.append("Shopen ain't open soz, go get your snacks elsewhere :(")
                gif = "Sad"
                return response, gif

            openTime = shopenData.val()["OpenTime"]
            shopenPerson = shopenData.val()["Name"]
            response.append(f"Shopen opened at {openTime}")
            response.append(f"{shopenPerson} is on shopen!")

            gif = "Yay"

        else:
            response.append("Shopen ain't open soz, go get your snacks elsewhere :(")
            gif = "Sad"
    
    return response, gif

def checkForEasterEggs(message):
    response = []
    gif = None

    if ("tall" in message or "height" in message) and ("sam" in message or "bensley" in message):
        if "really" in message:
            response.append("*cough* 5`11")
        else:
            response.append("6 foot")
    elif "bssrprdctns" in message or "basser productions" in message:
        response.append("Huge Content Coming Soon!")
    elif "dean" in message and "deputy" in message:
        response.append("THE DEPUTYYYY DEANNNNN")
        gif = "salute"
    elif "sam bensley" in message or "zoe bott" in message:
        response.append("did you mean: 'sexy alpha coders'")
    elif "easter egg" in message:
        response.append("go find em")
        gif = "easter egg"
    elif "baxter" in message:
        response.append("Get rekt Baxter")
        gif = "get rekt"
    elif "goldstein" in message:
        response.append("Basser is better")
        gif = "dab"
    elif "baxtabot" in message:
        response.append("Do you mean: 'less inferior bot'?")
        gif = "sorry not sorry"
    elif "zali" in message or "president" in message:
        response.append("Madame president")
        gif = "donald trump"
    elif "matthew" in message or "batesy" in message or "bates" in message or "matt" in message or "batesos" in message:
        response.append("Daenerys of the House Targaryen, the First of Her Name, The Unburnt, Queen of the Andals, the Rhoynar and the First Men, Queen of Meereen, Khaleesi of the Great Grass Sea, Protector of the Realm, Lady Regent of the Seven Kingdoms, Breaker of Chains and Mother of Dragons")
        gif = "dracarys"
    elif "wam" in message and "jodie" in message:
        response.append("Higher than yours")
    elif "meme" in message:
        response.append("")
        gif = "meme"
    elif "who would win in a fight" in message:
        try:
            person = message.split(' ')[6]
            response.append(f"{person.capitalize()} would clearly win.")
        except:
            response.append("Between who?") 
    return response, gif

def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    responseList, gif = get_bot_response(message)
    for response in responseList:
        send_message(sender, response)
    if gif:
        send_gif_message(sender, gif)
    
def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))\

def search_gif(text):
    #get a GIF that is similar to text sent
    payload = {'s': text, 'api_key': 'ey1oVnN1NGrtEDHFGBJjRj5AgegLFVeT', 'weirdness': 0}
    r = requests.get('http://api.giphy.com/v1/gifs/translate', params=payload)
    r = r.json()
    # sprint(r)
    try:
        url = r['data']['images']['original']['url']
    except:
        print('failed to get gif')

    return url


@app.route("/",methods=['GET','POST'])
def listen():
    """This is the main function flask uses to 
    listen at the `/webhook` endpoint"""
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id, text)

        return "ok"

def send_message(recipient_id, text):
    """Send a response to Facebook"""
    payload = {
        'message': {
            'text': text
        },
        'recipient': {
            'id': recipient_id
        },
        'notification_type': 'regular'
    }

    auth = {
        'access_token': PAGE_ACCESS_TOKEN
    }

    response = requests.post(
        FB_API_URL,
        params=auth,
        json=payload
    )

    return response.json()

def send_gif_message(recipient_id, message):
    gif_url = search_gif(message)

    data = json.dumps({
        "recipient": {"id": recipient_id},
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": gif_url
                }
            }}
    })

    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }

    headers = {
        "Content-Type": "application/json"
    }

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",
                      params=params, headers=headers, data=data)

#print(get_bot_response("whats for dino"));