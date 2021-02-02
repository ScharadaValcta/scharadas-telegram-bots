#für die BotAPI
import requests
#für easy Access to Telegram Bot api
import telepot
#für Pausen und die date umrechnung
from time import sleep,strftime,gmtime
#für den download
from wget import download
#für den remove der datei und cwd
from os import getcwd,mkdir,rename,path,remove
#für load_token
import json
from os.path import isdir,isfile
import os
#für zip datei von stickerpacks
import zipfile


botname = 'telegram-sticker-exporter-bot'

def has(dictionary,string):
    try:
        value = dictionary[string]
        return True
    except Exception as e:
        return False

def load_token():    
    token = ''
    try:
        with open(botname + '.token','r') as tokenfile:
            token = json.load(tokenfile)
    except Exception as e:
        if token == '':
            token = input('Bitte Telegram-Bot Token eingeben:')
            save = input('Soll der Token gespeichert werden.(j/n):')
            if save.lower() == 'j':
                with open(botname + '.token', 'w') as tokenfile:
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

        if has(update,"message"):
            message = update["message"]
            if has(message,"chat"):
                if has(message["chat"],"id"):
                    #chat_id benötigt man um die zipfile am ende zurückzuschicken
                    chat_id = message["chat"]["id"]

            if has(message,"sticker"):
                received_sticker = message["sticker"]
                stickerpack_raw = {"fallback":"dictionary"}

                if has(received_sticker,"set_name"):
                    set_name = received_sticker["set_name"]
                    url = "https://api.telegram.org/bot" + bot_token 
                    stickerpack_raw = requests.get(url + "/getStickerSet" + "?name=" + set_name).json()
                if has(stickerpack_raw,"result"):
                    stickerpack = stickerpack_raw["result"]
                    if has(stickerpack,"title"):
                        set_name += "_" + stickerpack["title"] 

                    if path.isfile(data_path + set_name + ".zip"):
                        remove(data_path + set_name + ".zip")

                    if has(stickerpack,"stickers"):
                        stickers = stickerpack["stickers"]
                        #Zip datei öffnen
                        zipper = zipfile.ZipFile(set_name + ".zip",'w')

                        for sticker in stickers:
                            if has(sticker,"thumb"):
                                if has(sticker["thumb"],"file_id"):
                                    #erstellung der url zum herunterladen des Stickers
                                    file_id = sticker["thumb"]["file_id"]
                                    fileurl = "https://api.telegram.org/file/bot" + bot_token + "/"                    
                                    fileinfo = bot.getFile(file_id)
                                    file = fileurl + fileinfo["file_path"]

                                    #sticker herunterladen
                                    filename = download(file)
                                    new_filename = filename
                                    if has(sticker,"emoji"):
                                        #emoji an den Filename vorne ranhängen damit der import einfacher wird
                                        new_filename = sticker["emoji"] + filename

                                    #heruntergeladener Sticker zur Zip hinzufügen
                                    zipper.write(data_path + filename,new_filename,zipfile.ZIP_DEFLATED)
                                    remove(data_path + filename)

                        #Zip datei schließen
                        zipper.close()
                        data_path_to_zip = data_path + set_name + ".zip"
                        compressed_file =  {'document': open(data_path_to_zip, 'rb')}

                        #Zipdatei zurücksenden
                        requests.post(url + "/sendDocument" + "?chat_id=" + str(chat_id),files=compressed_file)
        offset = update["update_id"] + 1
        sleep(sleeptime)





if __name__ == '__main__':
    main()