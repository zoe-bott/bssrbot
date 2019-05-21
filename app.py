from flask import Flask, request
import requests
from datetime import date
from Menu import *
import json

app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = 'letthebasseriansyeet'# <paste your verify token here>
PAGE_ACCESS_TOKEN = 'EAAidPSNIxU0BAAvOOuFF9VZAoQWqENQLMxGPC36A67YXcJfCZCVKNeUpZAkXboUwTOE61RwkzNbO3kQNtjlZAFhOtZBUt9zbKskKjCdh01Lk6fD0dwLXY7N6c8LxVR76QXFlf0RM6SFYAdflKZC1fYpgJonPziIJlmstlIw2wYbAZDZD'


def get_bot_response(message, sender):
    message = message.lower()
    response = []
    current_day = date.today().weekday()
    todayMenu = getDayMenu(current_day)
    if "dino" in message:
        response.append("For breakfast today is:")
        response.append(todayMenu.breakfast)

        response.append("For lunch today is:")
        response.append(str(todayMenu.lunch))

        response.append("For dinner today is:")
        response.append(str(todayMenu.dinner))
        send_gif_message(sender, "what's cooking")
    elif "breakfast" in message:
        response.append("For breakfast today is:")
        response.append(todayMenu.breakfast)
        send_gif_message(sender, "breakfast")
    elif "lunch" in message:
        response.append("For lunch today is:")
        response.append(str(todayMenu.lunch))
        send_gif_message(sender, "lunch")
    elif "dinner" in message:
        response.append("For dinner today is:")
        response.append(str(todayMenu.dinner))
        send_gif_message(sender, "dinner")
    elif "hello" in message or "hi" in message or "help" in message:
        response.append("Hello! Welcome to the Basser Bot! Ask me 'what's for dino' or 'what's for lunch' to get started")
        send_gif_message(sender, "hello")
    else:
        response.append("Sorry I don't understand")
        send_gif_message(sender, "sorry")

    return response


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message):
    """Formulate a response to the user and
    pass it on to a function that sends it."""
    responseList = get_bot_response(message, sender)
    for response in responseList:
        send_message(sender, response)
    
    

def is_user_message(message):
    """Check if the message is a message from the user"""
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))\

def search_gif(text):
    #get a GIF that is similar to text sent
    payload = {'s': text, 'api_key': 'KnoGs32vB6pMxyjAC3V22xWdWenz5asW', 'type': 'random'}
    r = requests.get('http://api.giphy.com/v1/gifs/translate', params=payload)
    r = r.json()
    url = r['data']['images']['original']['url']

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