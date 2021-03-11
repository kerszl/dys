import requests

link="http://mcdn-dwld.com/dock-station/download/2021/03/09/Fernando%20Ferreyra%20-%20Dreamers%20(March%202021).mp3"
#link="https://syndicast.co.uk/distribution/download/preview/uploads/audios/17/173-7.mp3"
r = requests.get(link, allow_redirects=True, stream=True)
#print (r.headers['content-length'])
if 'content-length' in r.headers:
    print (r.headers)