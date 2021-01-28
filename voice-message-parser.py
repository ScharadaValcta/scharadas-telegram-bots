#für die BotAPI
import requests
#für easy Access to Telegram Bot api
import telepot
#fürPausen
from time import sleep
#für die Umwandlung
import pydub
#für die Erkennung
import speech_recognition
#für den download
import wget
#für den remove der datei und cwd
import os
#für load_token
import json


def load_token():    
    token = ''
    try:
        with open('voice-message-parser.token','r') as tokenfile:
            token = json.load(tokenfile)
    except Exception as e:
        if token == '':
            token = input('Bitte Telegram-Bot Token eingeben:')
            save = input('Soll der Token gespeichert werden.(j/n):')
            if save.lower() == 'j':
                with open('voice-message-parser.token', 'w') as tokenfile:
                    json.dump(token, tokenfile)
    return token

def main():
    bot_token = load_token()
    bot = telepot.Bot(bot_token)
    offset = 0
    sleeptime = 1
    
    
    url = "https://api.telegram.org/bot" + bot_token 
    fileurl = "https://api.telegram.org/file/bot" + bot_token + "/"
    
    while True:
        try:
            update_raw = bot.getUpdates(offset)
        except:
            sleep(sleeptime)
            continue
    
        if update_raw == []:
            sleep(sleeptime)
            continue
        update = update_raw[0]
        
        try:
            #print(update[-1]["message"]["voice"])
            file_id = update["message"]["voice"]["file_id"]
        except Exception as e:
            sleep(sleeptime)
            continue
    
        #fileinfo = bot.getFile(file_id = file_id)
        #file = fileurl + fileinfo["file_path"]
    
        fileinfo = requests.get(url + "/getFile" + "?file_id=" + file_id).json()
        file = fileurl + fileinfo["result"]["file_path"]
    
        filename = wget.download(file)
    
        chat_id = update["message"]["chat"]["id"]
        text = "Fallback Text"
    
        data_path = os.getcwd() + "/"
        path_to_ogg = data_path + filename
        path_to_wav = data_path + filename + ".wav"
        lang = 'de-DE'
        
        #Convert
        sound = pydub.AudioSegment.from_ogg(
            path_to_ogg).export(path_to_wav, format="wav")
    
        #Removefile
        os.remove(path_to_ogg)
        
        #Recognizer
        recognizer = speech_recognition.Recognizer()
        google_audio = speech_recognition.AudioFile(
            path_to_wav)
        
        with google_audio as source:
            audio = recognizer.record(source)
        
        try:
            text = recognizer.recognize_google(audio, language=lang)
        except Exception as e:
            sleep(sleeptime)
            continue
    
        requests.post(url + "/sendMessage" + "?chat_id=" + str(chat_id) + "&text=" + text)
    
        #Removefile
        os.remove(path_to_wav)
        
        #print("<Erkannter Text>: {}".format(text))
        offset = update["update_id"] + 1
        sleep(sleeptime)

if __name__ == '__main__':
    main()