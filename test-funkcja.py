import re
import requests
from bs4 import BeautifulSoup as bs
from tqdm import tqdm


link_do_analizy="http://box.globaldjmix.com/media/matt-holliday-moments-042-2023-september-06/CzmW8P"

strona=requests.get(link_do_analizy)
strona=bs(strona.text,'html.parser')

strona=strona.find("a",{"class":"btn btn-success"})
print (strona['href'])

exit 


szukajW="http://box.globaldjmix.com/media/matt-holliday-moments-042-2023-september-06/CzmW8P"
szukaj="box.globaldjmix.com/"
a=re.search(szukaj,szukajW)


#print (a.pos)
#exit

if re.search(szukaj, szukajW):
    print("znalazlem")
    