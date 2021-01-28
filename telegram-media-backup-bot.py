#für easy Access to Telegram Bot api
import telepot
#für Pausen und die date umrechnung
from time import sleep,strftime,gmtime
#für den download
from wget import download
#für den remove der datei und cwd
from os import getcwd,mkdir,rename,path
#für load_token
import json
#from os.path import isdir
#import os

def has(dictionary,string):
    try:
        value = dictionary[string]
        return True
    except Exception as e:
        return False

def load_token():    
    token = ''
    try:
        with open('telegram-media-backup-bot.token','r') as tokenfile:
            token = json.load(tokenfile)
    except Exception as e:
        if token == '':
            token = input('Bitte Telegram-Bot Token eingeben:')
            save = input('Soll der Token gespeichert werden.(j/n):')
            if save.lower() == 'j':
                with open('telegram-media-backup-bot.token', 'w') as tokenfile:
                    json.dump(token, tokenfile)
    return token


def main():
    bot_token = load_token()
    bot = telepot.Bot(bot_token)
    
    offset = 0
    sleeptime = 1
    data_path = getcwd() + "/"
    
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
        #print(update["update_id"])
        #Zum extrahieren ohne Fehler des Namens
        if has(update,"message"):
            message = update["message"]
            #print(message)
            if has(message,"from"):
                frompart = message["from"]
                #In fullusername steht der volle Name mit username
                fullusername = ""
                fromname = ["first_name","last_name","username"]
                for chatpart in fromname:
                    if has(frompart,chatpart):
                        fullusername += frompart[chatpart] + "_"
                fullusername = fullusername[0:-1]
                messagetype = ""            
    
            if has(message,"forward_from"):
                forwardpart = message["forward_from"]
                #In fullusername steht der volle Name mit username
                fullusername = ""
                fromname = ["first_name","last_name","username"]
                for chatpart in fromname:
                    if has(forwardpart,chatpart):
                        fullusername += forwardpart[chatpart] + "_"
                fullusername = fullusername[0:-1]
                #print(fullusername)
                messagetype = "forwarded_"
    
            #In date steht Date the message was sent in Unix time
            unixdate = message["date"]
            if has(message, "forward_date"):
                unixdate = message["forward_date"]
            date = strftime('%Y_%m_%d_%H_%M_%S', gmtime(unixdate))
    
            if has(message,"chat") and has(message,"photo"):
                chat = message["chat"]
                messagetype += chat["type"]
                if chat["type"] == "private":
                    messagetype += "_" + fullusername
                if chat["type"] == "group":
                    if has(chat,"title"):
                        messagetype += "_" + chat["title"]
                #print(messagetype)
    
                if not path.isdir(data_path + messagetype):
                    mkdir(messagetype)
    
            if has(message,"photo"):
                photos = message["photo"]
                height = 0
                width = 0
                mul = height * width
    
                for photo in photos:
                    lmul = int(photo["height"]) * int(photo["width"])
                    if lmul > mul:
                        file_id = str(photo["file_id"])
                        lmul = int(photo["height"]) * int(photo["width"])
                fileinfo = bot.getFile(file_id)
                fileurl = "https://api.telegram.org/file/bot" + bot_token + "/"
                file = fileurl + fileinfo["file_path"]
                filename = download(file)
                rename(data_path + filename, data_path + messagetype + "/" + date + "_" + fullusername)
        offset = update["update_id"] + 1
        sleep(sleeptime)

#fdupes -r -S -t -d .
#nextcloud anbindung

if __name__ == '__main__':
    main()