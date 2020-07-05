# THE ONLY THING YOU NEED TO CHANGE IN THIS FILE IS INTRODUCING THE NEW DISEASES
# IN THE LIST diseases.

# THE REST IS UNTOUCHABLE
#===============================================================================

# import the Telegram API and several other modules
import telegram
from telegram.ext import Updater
from telegram.ext import MessageHandler, CommandHandler
from telegram.ext import Filters
import string
import os
from utils import process_message, read_book
from utils import get_keywords
from translate import *
from nltk.tokenize import word_tokenize
from googletrans import Translator


# Modules needed for the hospitals location feature:
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import json
import math
from math import *

# This function can find the coordinates of a place from its name.
geolocator = Nominatim()

#===============================================================================

# add here the name of any disease you can provide info about
# then run the functions aaaaaaaaaaa("name_of_the_new_disease") to create the
# .json files for this disease.
# Congratulations, you added a disease to the database.

diseases = ['melanoma',]
users = []

first = True
specified_disease = False

def onMessage(bot, update, user_data):


    global first
    global specified_disease
    global data
    global information_hospitals
    global lat
    global lon

    if update.message.chat.id not in users:
        users.append(update.message.chat.id)
    else:
        first = False

    if first: # First time, it displays a presentation message
        username = update.message.chat.first_name
        if username is None:
            username = " "
        else:
            username = " " + username

        first = False
        msg=tr2english(update.message.text.lower(), user_data)
        message1 = "Hi" + username + "! I'm your Health Mate. I'm here to inform you about rare diseases. Please don't hesitate to ask me any question you have about it, I'll try my best to answer your doubts using trustful sources. Remember that I'm just here to inform you; for anything else contact a professional."
        message2 = "First of all, I would like you to tell me which disease you want to find out about. Please, tell me the name of the disease."
        bot.send_message(chat_id=update.message.chat_id, text = tr2other(message1, user_data['language']))
        bot.send_message(chat_id=update.message.chat_id, text = tr2other(message2, user_data['language']))
        specified_disease = False
        return

    else:
        msg=tr2english(update.message.text.lower(), user_data)
        keywords=get_keywords(msg)
        if specified_disease==False:
            for i in diseases:
                if i in msg:
                    data = read_book("main_data_"+i+".json")
                    information_hospitals = read_book('hospitals_information_'+i+'.json')
                    message = "Perfect!. I understand you asked about "+i+". From now on we will be talking about this disease in particular."
                    message2a = "If I did not understand it wel, or you wish to change the subject, you can type"
                    message2b = "and I will ask again."
                    bot.send_message(chat_id=update.message.chat_id, text = tr2other(message, user_data['language']))
                    bot.send_message(chat_id=update.message.chat_id, text = tr2other(message2a, user_data['language'])+' /disease '+tr2other(message2b, user_data['language']) )
                    bot.send_message(chat_id=update.message.chat_id, text = tr2other('You can ask me any question related to this disease.', user_data['language']))
                    bot.send_message(chat_id=update.message.chat_id, text = tr2other('You can also send me your location and I will find the closest hospital where this disease can be diagnosed and treated.', user_data['language']))
                    bot.send_message(chat_id=update.message.chat_id, text = tr2other('You can type in', user_data['language'])+' /help '+tr2other('To know about all the text commands.', user_data['language']))
                    specified_disease = True
                    return
                else:
                    bot.send_message(chat_id=update.message.chat_id, text = tr2other("Sorry, I did not understand you. Please try again. The diseases I have information about are: "+diseases[0]+'.', user_data['language']))
                    return



        elif 'hello' in keywords or 'hi' in keywords or 'greetings' in keywords:

            bot.send_message(chat_id=update.message.chat_id, text=tr2other("Hello!", user_data['language']))

        elif 'bye' in keywords or 'goodbye' in keywords:

            bot.send_message(chat_id=update.message.chat_id, text=tr2other("Goodbye! Thanks for trusting me.", user_data['language']))

        elif 'thank' in keywords or 'appreciate' in keywords or 'thanks' in keywords:

            bot.send_message(chat_id=update.message.chat_id, text=tr2other("You are welcome! I am always trying to give my best", user_data['language']))

        else:
            message = tr2other('Okay, give me some time to think about it...', user_data['language'])
            bot.send_message(chat_id=update.message.chat_id, text = message, parse_mode = telegram.ParseMode.MARKDOWN)

            info = process_message(update.message['text'], data)
            if info:
                source_message = f"In case you want more information about it, the information I found comes from this source:\n `{info['URL']}` \n From the section *{info['title']}*"
                answer = f"Alright! I found the following information: \n \n {info['text']}"
                bot.send_message(chat_id=update.message.chat_id, text = tr2other(answer, user_data['language']), parse_mode = telegram.ParseMode.MARKDOWN)
                bot.send_message(chat_id=update.message.chat_id, text = tr2other(source_message, user_data['language']), parse_mode = telegram.ParseMode.MARKDOWN)
            else:
                error_msg = 'I am sorry, but I cannot answer this properly. You can try asking it a different way or contact a specialist for further information'
                bot.send_message(chat_id=update.message.chat_id, text = tr2other(error_msg, user_data['language']), parse_mode = telegram.ParseMode.MARKDOWN)



def giveClosestHospital(bot, update, user_data):
    try:
        global lat
        global lon
        lat = update.message.location.latitude
        lon = update.message.location.longitude
        hospitals = findHospitalsCountry(lat,lon)
        if hospitals != []:
            closest=[100000000,'Hospital']
            for i in hospitals:
                if i[0]<closest[0]:
                    closest = i
        else:
            bot.send_message(chat_id=update.message.chat_id, text=tr2other('I am sorry, there are no hospitals that treat this desease in your country.', user_data['language']))
        closest_hospital = geolocator.geocode(closest[1])
        lat, lon = closest_hospital.latitude, closest_hospital.longitude

        bot.send_location(chat_id=update.message.chat_id, latitude=lat, longitude=lon)

        text = "This is the location of the nearest hospital in you country in which this disease can be treated.\nThis hospital is " + closest_hospital.address
        bot.send_message(chat_id=update.message.chat_id, text=tr2other(text, user_data['language']))
        bot.send_message(chat_id=update.message.chat_id, text=tr2other('If you wish to know about more hospitals in your country that can treat this disease, you can type in ', user_data['language'])+' \AllHospitals '+tr2other('for a full list of them.', user_data['language']))
    except Exception as e:
        print(e)

def findHospitalsCountry(lat, long):
    list = []
    latlon_country = geolocator.reverse(lat, long).address.split(', ')[-1]
    for i in range(0, len(information_hospitals)):
        hospital = information_hospitals[i]
        lat2 = hospital['lat']
        long2 = hospital['lon']
        distance = geodesic((lat,long),(lat2,long2)).kilometers
        if hospital['country'] == latlon_country:
            list.append([distance,hospital['name']])
    return list


def disease(bot, update, user_data):
    global specified_disease
    specified_disease = False
    bot.send_message(chat_id=update.message.chat_id, text=tr2other('Reset! Now please tell me which other disease you want to find out about.', user_data['language']))

def start(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id, text='Hello! Hola! Bonjour!')
    bot.send_message(chat_id=update.effective_chat.id, text='You can talk to me in any language you want, I understand all of them! Please send a text in you language so that I can learn it.')
    bot.send_message(chat_id=update.effective_chat.id, text='Puedes hablar conmigo en el idioma que quieras, ¡los entiendo a todos! Por favor envíe un texto en su idioma para que pueda aprenderlo.')
    del user_data['language']
    first=True

def allhosp(bot, update):
    global lat
    global lon
    a=findHospitalsCountry(lat, lon)
    for i in a:
        location=geolocator.geocode(i[1].strip("\n"))
        text=str(location)
        print(text)
        address = geolocator.reverse(location.latitude, location.longitude ).address
        bot.send_message(chat_id=update.message.chat_id, text = text)
    pass

def help(bot, update, user_data):
    bot.send_message(chat_id=update.message.chat_id, text=tr2other('You can use the following commands.',  user_data['language']))
    bot.send_message(chat_id=update.message.chat_id, text='/start : ' + tr2other('To change the language.',  user_data['language']))
    bot.send_message(chat_id=update.message.chat_id, text='/disease : ' + tr2other('To change the disease you want information about.',  user_data['language']))
    bot.send_message(chat_id=update.message.chat_id, text='/AllHospitals : ' + tr2other('To know the full list of hospitals in your country that can diagnose and treat the selected disease.',  user_data['language']))


TOKEN = open('./token.txt').read().rstrip()

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('AllHospitals', allhosp))
dispatcher.add_handler(CommandHandler('disease', disease, pass_user_data=True))
dispatcher.add_handler(CommandHandler('start', start, pass_user_data=True))
dispatcher.add_handler(CommandHandler('help', help, pass_user_data=True))

dispatcher.add_handler(MessageHandler(Filters.text, onMessage, pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.location, giveClosestHospital, pass_user_data=True))


updater.start_polling()
