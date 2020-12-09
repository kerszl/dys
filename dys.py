#!/usr/bin/python3
import login_data
"""
touch file "login_data.py"
write to file your content like:"

username_field="login"
password_field = "password"
username = "here_your_login"
password = "here_your_password"
param={username_field:username,password_field:password,}


"""

from datetime import datetime
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm
import re
from pathlib import Path, PureWindowsPath
import json
import yaml
from time import sleep
from random import randrange


SITE='https://globaldjmix.com'
MAIN_LOGIN="https://globaldjmix.com/user?page=auth-form-action"
SEARCH_SITE="https://globaldjmix.com/search-result?search=eelke"
FAVORITE_DJS=['Hernan Cattaneo','Lemon8'] 
#rzedami a-f,g-l,m-r,s-x
#przerobilem na ladowanie

NF_djs_DH=[]
NF_djs_PH=[]
NF_djs_AM=[]
NF_djs_CH=[]
NOT_FAVORITE_DJS=[]

JSON_DOWNLOADED='downloaded.json'

NF_djs_files={
'NF_djs_DH_file':'not_favorite_djs_dh.json',
'NF_djs_PH_file':'not_favorite_djs_ph.json',
'NF_djs_AM_file':'not_favorite_djs_am.json',
'NF_djs_CH_file':'not_favorite_djs_ch.json'
}

def load_downloaded(file):        
    try:
        with open(file, 'r') as f:
            download_files_=json.load(f)            
    except ValueError as e:                
        print ("Problem z plikiem "+file+" lub formatem json")
        print (e)        
        exit()
    return download_files_

def save_downloaded(data,file):        
    try:
        with open(file, 'w') as f:
            json.dump(data,f)
    except ValueError as e:                
        print ("Problem z plikiem "+file+" lub formatem json")
        print (e)        
        exit()



#https://globaldjmix.com/user
#login=kerzon&password=niechcezmieniachasla10
#MAIN_LOGIN="https://globaldjmix.com/user"
#MAIN_LOGIN=r'https://globaldjmix.com/user?page=auth-form-action&type=ajax'
#MAIN_LOGIN='https://globaldjmix.com/user?page=auth-form-action&type=ajax'



def check_json_file():
    file_json_exists=Path(MP3_SAVE_DIRECTORY+JSON_DOWNLOADED)
    download_files={}

    if not file_json_exists.exists():    
        save_downloaded(download_files,MP3_SAVE_DIRECTORY+JSON_DOWNLOADED)
    else:
        download_files=load_downloaded(MP3_SAVE_DIRECTORY+JSON_DOWNLOADED)
    return download_files


def check_json_NF_djs_files():
    for i,file in NF_djs_files.items():        
        file_json_exists=Path(file)
        if not file_json_exists.exists():    
            print ('No file:',file)
        else:
            try:
                with open(file, 'r') as f:
                    if file=='not_favorite_djs_dh.json':
                        global NF_djs_DH
                        NF_djs_DH=json.load(f)
                    if file=='not_favorite_djs_ph.json':
                        global NF_djs_PH
                        NF_djs_PH=json.load(f)
                    if file=='not_favorite_djs_am.json':
                        global NF_djs_AM
                        NF_djs_AM=json.load(f)
                    if file=='not_favorite_djs_ch.json':
                        global NF_djs_CH
                        NF_djs_CH=json.load(f)                                        
            except ValueError as e:                
                print ("Problem z plikiem "+file+" lub formatem json")
                print (e)        
                exit()
    global NOT_FAVORITE_DJS
    NOT_FAVORITE_DJS=NF_djs_DH+NF_djs_PH+NF_djs_AM+NF_djs_CH

    



#session=requests.Session()
login_headers = {
    'x-requested-with': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded', # its urlencoded instead of form-data
    #'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'User-agent':'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0',
    
}
#r=requests.head(login_headers)
#r=requests.Session()
def first_login():
    first_login_=requests.post(MAIN_LOGIN, data=login_data.payload,headers=login_headers)    
    cookie=first_login_.cookies
    return cookie

def read_site():    
    #z sesja chyba zmiana naglowaka nie dziala
    print ("Wczytuje:",MUSIC_SITE)
    read_site=requests.get(MUSIC_SITE,cookies=cookie)
    return read_site
    #read_site=requests.get(SEARCH_SITE,cookies=cookie)
    #s=r.get(MUSIC_SITE)
    #print (s.request.headers)
    


#---zgraj liste dj-ow z głownego panela
def zgraj_liste_dj():
    main_panel=bs(read_site.text,'html.parser')
    #nieaktualnne    
    #b=a.find("div",{"class":"mixes-list-wrapper clearfix"})
    main_panel=main_panel.find("div",{"class":"col-md-9 single-panel-wrapper"})
    main_panel=main_panel.find_all("div",{"class":"mix-title"})    

    djs={}
    #print ("Nowe sety:")
    for i in main_panel:
        j=i.text.strip()        
        k=i.a['href'].strip()
        djs[k]=j
    #   print (j,k)
    return djs


#wejdz na podstrone i pozgrywaj mixy
BAD_FILE_CHAR =[":",".","?",",","\\","/"]
CAN_DOWNLOAD_FILE_HEADER=['audio/mpeg','application/octet-stream']

def can_download_dj (mp3_file):
    can_download=True
    for i in NOT_FAVORITE_DJS:        
        string_compile='^'+i.lower()+'.*'                
        a=re.search(string_compile,mp3_file.lower())        
        if a:
            can_download=False                  
    return can_download

#---glowna petla
def main_loop(djs_):
    set_count=0
    for set_site_links,mp3_file_write in djs_.items():
        #set_site_links_ORIG=set_site_links.replace("/livedjsets/","")

        set_site_links=SITE+set_site_links
        #set_site_links=SITE+list(djs.keys())[0]
        for i in BAD_FILE_CHAR:
            mp3_file_write=mp3_file_write.replace(i,"_")

        mp3_file_write=mp3_file_write+".mp3"
        mp3_file_write_DIR=MP3_SAVE_DIRECTORY+mp3_file_write

        mp3_site_download=requests.get(set_site_links,cookies=cookie)
        mp3_site_download=bs(mp3_site_download.text,'html.parser')

        mp3_site_download=mp3_site_download.find("div",{"class":"download_source"})
        mp3_site_download=mp3_site_download.find("div",{"class":"link-wrapper-zippy"})

        link_download=mp3_site_download.a['href']
        #Odczekiwanie, żeby pomysleli, że to człowiek        
        time_sleep=randrange(3,15)
        print (mp3_file_write_DIR)
        print ("Czekam",time_sleep,"sekund")        
        sleep(time_sleep)        
        
        
        #FILE_EXISTS=Path(mp3_file_write_DIR)
        if not mp3_file_write in download_files:
        #if not FILE_EXISTS.exists():        
            r = requests.get(link_download, allow_redirects=True, stream=True)
            #sprawdzamy czy mozna sciagnac
            #if (r.headers['Content-Type']=='audio/mpeg' or r.headers['Content-Type']=='application/octet-stream'):        
            #if NOT_FAVORITE_DJS            
            if can_download_dj(mp3_file_write):        
            
                if r.headers['Content-Type'] in CAN_DOWNLOAD_FILE_HEADER:
                                    
                    total_size_in_bytes= int(r.headers['content-length'])
                    block_size = 1024 #1 Kibibyte
                    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)

                    #print ("Zapisuje: ",mp3_file_write)
                    print ("\nSciagam z:",link_download)
                    with open(mp3_file_write_DIR, 'wb') as file:    
                        for data in r.iter_content(block_size):
                            progress_bar.update(len(data))        
                            file.write(data)
                    progress_bar.close()
                    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
                        print("ERROR: cos poszło zle przy zapisie")
                    else:                
                        download_files[mp3_file_write]=datetime.now().strftime("%d%m%Y")
                        save_downloaded(download_files,MP3_SAVE_DIRECTORY+JSON_DOWNLOADED)
                        set_count+=1                        
                else:
                    print (link_download,"- to nie bezposredni plik")
            else:
                print ("Nielubiany dj: ")
        else:
            print ("Sciagnalem wczesniej ten plik")
        print ("")
    if set_count==1:
        print ('Sciagnalem',set_count,'set.')
    else:
        print ('Sciagnalem',set_count,'setow')


def przetasuj (djs):    
    d_set=list(set(djs))
    return {i:djs[i] for i in d_set}


#-------------------------------------------------------------------------------

#Windows
#--ambient 
#MUSIC_SITE="https://globaldjmix.com/style-mixes/ambient"
#MP3_SAVE_DIRECTORY='E:\\!new\\dys - sety\\ambient\\'
#--chillout site
#MUSIC_SITE="https://globaldjmix.com/style-mixes/chillout"
#MP3_SAVE_DIRECTORY='E:\\!new\\dys - sety\\chillout\\'
#--deep-house
#MUSIC_SITE="https://globaldjmix.com/style-mixes/deep-house"
#MP3_SAVE_DIRECTORY='E:\\!new\\dys - sety\\deep-house\\'
#--progressive house site
#MUSIC_SITE="https://globaldjmix.com/style-mixes/progressive-house"
#MP3_SAVE_DIRECTORY='E:\\!new\\dys - sety\\progressive-house\\'

#--------------Linux-----------------
#--ambient 
#MUSIC_SITE="https://globaldjmix.com/style-mixes/ambient"
#MP3_SAVE_DIRECTORY='/mnt/e/!new/dys - sety/ambient/'
#--chillout site
#MUSIC_SITE="https://globaldjmix.com/style-mixes/chillout"
#MP3_SAVE_DIRECTORY='/mnt/e/!new/dys - sety/chillout/'
#--deep-house
#MUSIC_SITE="https://globaldjmix.com/style-mixes/deep-house"
#MP3_SAVE_DIRECTORY='/mnt/e/!new/dys - sety/deep-house/'
#--progressive house site
MUSIC_SITE="https://globaldjmix.com/style-mixes/progressive-house"
MP3_SAVE_DIRECTORY='/mnt/e/!new/dys - sety/progressive-house/'

#-------------------------------------------------------------------------------

#--------main program-------

check_json_NF_djs_files()
download_files=check_json_file()
cookie=first_login()
read_site=read_site()
djs=zgraj_liste_dj()
djs=przetasuj(djs)

main_loop(djs)
