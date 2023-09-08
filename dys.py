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

#rzedami a-f,g-l,m-r,s-x
#przerobilem na ladowanie

NF_djs_DH=[]
NF_djs_PH=[]
NF_djs_AM=[]
NF_djs_CH=[]
NOT_FAVORITE_DJS=[]
FAVORITE_DJS=[]

JSON_DOWNLOADED='downloaded.json'
YAML_SITE='site_download.yaml'

#nielubiani dj-e
NF_djs_files={
'NF_djs_DH_file':'not_favorite_djs_dh.json',
'NF_djs_PH_file':'not_favorite_djs_ph.json',
'NF_djs_AM_file':'not_favorite_djs_am.json',
'NF_djs_CH_file':'not_favorite_djs_ch.json'
}

#lubiani dj-e (nawet jak sa w nielubianych to i tak sciagaj)
F_djs_files={
    'F_djs_file':'favorite_djs.json'
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


#sprawdz czy jest plik z zapisem sciagnietych setow
def check_json_file():
    file_json_exists=Path(MP3_SAVE_DIRECTORY+JSON_DOWNLOADED)
    download_files={}

    if not file_json_exists.exists():    
        save_downloaded(download_files,MP3_SAVE_DIRECTORY+JSON_DOWNLOADED)
    else:
        download_files=load_downloaded(MP3_SAVE_DIRECTORY+JSON_DOWNLOADED)
    return download_files

#sprawdz czy jest plik z rodzajem muzyki, ktora ma sciagac
def check_yaml_file (YAML_SITE):
    file_yaml_exists=Path(YAML_SITE)
    if not file_yaml_exists.exists():
        print ("Nie ma pliku",YAML_SITE)
        exit ()
    with open(YAML_SITE, 'r') as f:            
        download_files_=yaml.load(f,Loader=yaml.SafeLoader)    
    for i in download_files_:
        if len (download_files_[i]) !=2:
            print ("Sprawdz: ",YAML_SITE)
            exit ()
            

    

def load_site_download (YAML_SITE):    
    #bez try i tak wszystko prawie wczyta, wczesniej jest sprawdzanie
    with open(YAML_SITE, 'r') as f:            
        download_files_=yaml.load(f,Loader=yaml.SafeLoader)    
    return download_files_

#sprawdz czy sa pliki z nielubianymi dj-jami
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

    
#sprawdz czy jest plik z ulubianymi dj-jami (bez kategorii)

def check_json_F_djs_files():
    file=F_djs_files['F_djs_file']
    file_json_exists=Path(file)
    if not file_json_exists.exists():    
        print ('No file:',file)
    else:
        try:
            with open(file, 'r') as f:                    
                global FAVORITE_DJS
                FAVORITE_DJS=json.load(f)
        except ValueError as e:                
            print ("Problem z plikiem "+file+" lub formatem json")
            print (e)        
            exit()
    



#session=requests.Session()
login_headers = {
    'x-requested-with': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded', # its urlencoded instead of form-data
    #'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.129 Safari/537.36',
    'User-agent':'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/86.0',
    
    
}
#r=requests.head(login_headers)
#r=requests.Session()
def first_login():
    try:
        first_login_=requests.post(MAIN_LOGIN, data=login_data.payload,headers=login_headers)    
        cookie=first_login_.cookies
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print ("Nie moge się polaczyć z ",MAIN_LOGIN)        
        raise SystemExit(e)        
    return cookie

def read_site():    
    #z sesja chyba zmiana naglowaka nie dziala
    print ("Wczytuję:",MUSIC_SITE)
    try:
        read_site_=requests.get(MUSIC_SITE,cookies=cookie)
    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print ("Nie moge się polaczyć z: ",MUSIC_SITE)
        raise SystemExit(e)

    
    return read_site_
    #read_site=requests.get(SEARCH_SITE,cookies=cookie)
    #s=r.get(MUSIC_SITE)
    #print (s.request.headers)
    


#---zgraj liste dj-ow z głownego panela
def zgraj_liste_dj():
    main_panel=bs(read_site_.text,'html.parser')    
    #nieaktualnne    
    #b=a.find("div",{"class":"mixes-list-wrapper clearfix"})
    #main_panel=main_panel.find("div",{"class":"col-md-9 single-panel-wrapper"})
    #main_panel=main_panel.find("div",{"class":"single-panel col-md-9 single-panel-wrapper"})
    main_panel=main_panel.find("div",{"class":"mixes-list-wrapper clearfix"})    
    #main_panel=main_panel.find_all("div",{"class":"mix-title"})    
    main_panel=main_panel.find_all('a',href=True)
    #print (main_panel[1].get('href'))

    
    
#    for i in main_panel:
#        k=i.get('href').strip()
#        if (k.find('javascript:void(0)')):      
#            j=i.text.strip()      
#            print (j,'\n',k)
            #k=i.text
            #print (k)


        #k=i.a['href'].strip()
        #djs[k]=j
    
    

    djs={}
#    for i in main_panel:
#        j=i.text.strip()        
#        k=i.a['href'].strip()
#        djs[k]=j
    for i in main_panel:
            k=i.get('href').strip()
            #wyeliminowujemy javascript
            if (k.find('javascript:void(0)')):      
                j=i.text.strip()  
                djs[k]=j
                #print (j,'\n',k)
    return djs


#wejdz na podstrone i pozgrywaj mixy
BAD_FILE_CHAR =[":",".","?",",","\\","/"]
CAN_DOWNLOAD_FILE_HEADER=['audio/mpeg','application/octet-stream']

def can_download_dj (mp3_file):
    can_download="Nie znalazlem go w pliku"
    for i in NOT_FAVORITE_DJS:        
        string_compile='^'+i.lower()+'.*'                
        nielubiany_dj=re.search(string_compile,mp3_file.lower())        
        if nielubiany_dj:
            #can_download=False
            can_download=i
    return can_download

#---glowna petla
downloaded_report ={}
set_count=0
def main_loop(djs_,genre):
    
    global downloaded_report
    for set_site_links,mp3_file_write in djs_.items():
        #set_site_links_ORIG=set_site_links.replace("/livedjsets/","")

        set_site_links=SITE+set_site_links
        
        for i in BAD_FILE_CHAR:
            mp3_file_write=mp3_file_write.replace(i,"_")

        mp3_file_write=mp3_file_write+".mp3"
        mp3_file_write_DIR=MP3_SAVE_DIRECTORY+mp3_file_write

        mp3_site_download=requests.get(set_site_links,cookies=cookie)
        mp3_site_download=bs(mp3_site_download.text,'html.parser')

        mp3_site_download=mp3_site_download.find("div",{"class":"download_source"})
        mp3_site_download=mp3_site_download.find("div",{"class":"link-wrapper-zippy"})
        
        link_download=mp3_site_download.a['href']

        nowa_strona_link="box.globaldjmix.com/"
        
        
        if re.search(nowa_strona_link,link_download):
            mp3_site_download=requests.get(link_download)
            mp3_site_download=bs(mp3_site_download.text,'html.parser')
            mp3_site_download=mp3_site_download.find("a",{"class":"btn btn-success"})
            link_download=mp3_site_download['href']
            
                    
        #Odczekiwanie, żeby pomysleli, że to człowiek        
        time_sleep=randrange(3,15)        
        print (mp3_file_write_DIR)
        
        
        #if mp3_site_download is not None:
        if link_download is not None:        
            #link_download=mp3_site_download.a['href']            
            #FILE_EXISTS=Path(mp3_file_write_DIR)
            if not mp3_file_write in download_files:
            #if not FILE_EXISTS.exists():        
                r = requests.get(link_download, allow_redirects=True, stream=True)
                #sprawdzamy czy mozna sciagnac
                #if (r.headers['Content-Type']=='audio/mpeg' or r.headers['Content-Type']=='application/octet-stream'):        
                #if NOT_FAVORITE_DJS
                nielubiany_dj=can_download_dj(mp3_file_write)
                #Strasznie glupi warunek
                if nielubiany_dj == "Nie znalazlem go w pliku":        
                
                    if r.headers['Content-Type'] in CAN_DOWNLOAD_FILE_HEADER and 'content-length' in r.headers:                                    
                                        
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
                            global set_count
                            set_count+=1                        
                            #downloaded_report.append(mp3_file_write)
                            downloaded_report[mp3_file_write]=genre
                            print ("Czekam",time_sleep,"sekund")        
                            sleep(time_sleep)                                        
                    else:
                        if r.headers['Content-Type'] not in CAN_DOWNLOAD_FILE_HEADER:
                            print (link_download,"- to nie bezposredni plik")
                        else:                    
                            print (link_download,"- problem z okresleniem wielkosci")
                                                                            
                else:
                    print ("Nielubiany dj: ",nielubiany_dj)

            else:
                print ("Sciagnalem wczesniej ten plik")
        else:
            print ("Nie widze linku")
    

def przetasuj (djs):    
    d_set=list(set(djs))
    return {i:djs[i] for i in d_set}

def remove_favorite_from_not_favorite():
    global FAVORITE_DJS
    global NOT_FAVORITE_DJS
    for i in FAVORITE_DJS:        
        if i in NOT_FAVORITE_DJS:        
            NOT_FAVORITE_DJS.remove(i)
    return NOT_FAVORITE_DJS


def display_stats():
    global downloaded_report
    global set_count

    print ("\nSety ktore sciagnalem:")        
    for i,j in downloaded_report.items():
        print (i,":",j)
    
    if set_count==1:
        print ('\nSciagnalem',set_count,'set.\n')
    else:
        print ('\nSciagnalem',set_count,'setow.\n')


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
#MUSIC_SITE="https://globaldjmix.com/style-mixes/progressive-house"
#MP3_SAVE_DIRECTORY='/mnt/e/!new/dys - sety/progressive-house/'
MUSIC_SITE=""
MP3_SAVE_DIRECTORY=""
#MUSIC_DOWNLOAD_SITES={"ambient":["https://globaldjmix.com/style-mixes/ambient","/mnt/e/!new/dys - sety/ambient/"],
#                      "chilout":["https://globaldjmix.com/style-mixes/chillout","/mnt/e/!new/dys - sety/chillout/"],
#                      "deep-house":["https://globaldjmix.com/style-mixes/deep-house","/mnt/e/!new/dys - sety/deep-house/"],
#                      "progressive-house":["https://globaldjmix.com/style-mixes/progressive-house","/mnt/e/!new/dys - sety/progressive-house/"],
#                      }

#MUSIC_DOWNLOAD_SITES={}


#-------------------------------------------------------------------------------
#--------main program-------
#check_json_F_djs_files()
#check_json_NF_djs_files()
#remove_favorite_from_not_favorite()
#print (FAVORITE_DJS)
#print (NOT_FAVORITE_DJS)


check_yaml_file (YAML_SITE)
MUSIC_DOWNLOAD_SITES=load_site_download (YAML_SITE)

check_json_F_djs_files()
check_json_NF_djs_files()
remove_favorite_from_not_favorite()
#usun lubianych dj-ow z nielubianej listy

cookie=first_login()



for i in MUSIC_DOWNLOAD_SITES:
    MUSIC_SITE=MUSIC_DOWNLOAD_SITES[i][0]
    MP3_SAVE_DIRECTORY=MUSIC_DOWNLOAD_SITES[i][1]
    download_files=check_json_file()
    read_site_=read_site()
    djs=zgraj_liste_dj()
    djs=przetasuj(djs)
    main_loop(djs,i)

display_stats()
