from bs4 import BeautifulSoup as bs
import subprocess
import requests
import hashlib
import hmac
import uuid
import json
import time
import sys

AUTO_MODE = True

#Stolen from YTDL
AKAMAI_ENCRYPTION_KEY = None
if not AKAMAI_ENCRYPTION_KEY:
    print("No encryption key, can't proceed")
    sys.exit(0)
def bruh():
    st = int(time.time())
    exp = st + 6000
    auth = f'st={st}~exp={exp}~acl=/*'
    auth += '~hmac=' + hmac.new(AKAMAI_ENCRYPTION_KEY, auth.encode(), hashlib.sha256).hexdigest()
    return(auth)
def kek():
    st = int(time.time())
    exp = st + 6000
    auth = f'st={st}~exp={exp}~acl=/um/v3/*'
    auth += '~hmac=' + hmac.new(AKAMAI_ENCRYPTION_KEY, auth.encode(), hashlib.sha256).hexdigest()
    return(auth)
#End of stolen code

hotstar = requests.Session()

ID = input("Enter ID: ")

#USERTOKEN
USERTOKEN_HEADERS = {
                    "hotstarauth": kek(),
                    "x-hs-platform": "web",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
                    "origin": "https://www.hotstar.com",
                    "referer": "https://www.hotstar.com/"
                    }

USERTOKEN_PAYLOAD = {
                    "device_ids": [
                        {
                            "id": str(uuid.uuid4()),
                            "type": "device_id"
                        }
                    ],
                    "device_meta": {
                        "network_operator": "4g - 5.5 - 150",
                        "os_name": "Windows",
                        "os_version": "10"
                    }
                }

users_resp = hotstar.post('https://api.hotstar.com/um/v3/users', headers= USERTOKEN_HEADERS, json=USERTOKEN_PAYLOAD).json()

print(json.dumps(users_resp, indent=4))

#API
API_URL = f"https://api.hotstar.com/play/v2/playback/content/{ID}"

API_HEADERS = {
            "origin": "https://www.hotstar.com",
            "referer": "https://www.hotstar.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36",
            "hotstarauth": bruh(),
            "x-hs-appversion": "7.26.0",
            "x-hs-platform": "web",
            "x-hs-usertoken": users_resp["user_identity"]
        }

API_QUERY = {
            "device-id": uuid.uuid4(),
            "desired-config": "audio_channel:stereo|dynamic_range:sdr|encryption:widevine|ladder:tv|package:dash|resolution:hd|video_codec:h264",
            "os-name": "Windows",
            "os-version": "10"
        }

api_resp = hotstar.get(API_URL, headers=API_HEADERS, params=API_QUERY).json()

print(json.dumps(api_resp, indent=4))

#MPD
MPD_HEADERS = {
            "origin": "https://www.hotstar.com",
            "referer": "https://www.hotstar.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"
        }   

mpd_name = "master-tv.mpd"
m3u8_name = "master.m3u8"
mpd_url = None
m3u8_url = None


if AUTO_MODE:
    mpd_name = "master-tv.mpd"
    m3u8_name = "master.m3u8"
else:
    mpd_name = input("MPD Name: ")

for i in api_resp["data"]["playBackSets"]:
    if mpd_name in i["playbackUrl"]:
        mpd_url = i["playbackUrl"]
        break
    if m3u8_name in i["playbackUrl"]:
        m3u8_url = i["playbackUrl"]
        break

if not mpd_url:
    playlist_base = m3u8_url.split(m3u8_name)[0]
    m3u8 = hotstar.get(m3u8_url, headers=MPD_HEADERS).text
    print(bs(m3u8, "html.parser").prettify())
    stream_ids = []
    for i in m3u8.split('\n'):
        if "http" in i:
            stream_ids.append(i.replace(playlist_base, ""))

    if AUTO_MODE:
        stream_id = stream_ids[-1]
    else:
        stream_id = input("Index Name: ")

    index_url = playlist_base + stream_id
    index = hotstar.get(index_url, headers=MPD_HEADERS).text
    print(bs(index, "html.parser").prettify())
    
    segment_ids = []
    for i in index.split('\n'):
        if "http" in i:
            segment_ids.append(i.replace(playlist_base, ""))

    with open(f"{ID}.ts", "wb") as strm:
        for i in segment_ids:
            TS = hotstar.get(playlist_base + i, headers=MPD_HEADERS)
            if TS.status_code == 200:
                print(f"OK: {ID}-{i}")
                strm.write(TS.content)
                
    subprocess.run(["ffmpeg",
                    "-i", f"{ID}.ts", 
                    "-map", "0",
                    "-c", "copy",
                    f'{ID}.mp4'])

else:
    playlist_base = mpd_url.split(mpd_name)[0]
    mpd = hotstar.get(mpd_url, headers=MPD_HEADERS).content

    print(bs(mpd, "html.parser").prettify())

    video_ids = []
    audio_ids = []

    for i in bs(mpd, "lxml").find_all("representation"):
        if "video" in i.get("id"):
            video_ids.append(i.get("id"))
        elif "audio" in i.get("id"):
            audio_ids.append(i.get("id"))

    print(video_ids)
    print(audio_ids)

    if AUTO_MODE:
        video_id = video_ids[-1]
        audio_id = audio_ids[-1]
    else:
        video_id = input("Video ID: ")
        audio_id = input("Audio ID: ")  
        
    video_base_url = f"{mpd_url.split(mpd_name)[0]}{video_id}/"
    audio_base_url = f"{mpd_url.split(mpd_name)[0]}{audio_id}/"



    #DOWNLOAD
    with open(f"{ID}-vid.m4s", "wb") as vid:
        c = 1
        INIT = hotstar.get(video_base_url + "init.mp4", headers=MPD_HEADERS)
        print(f"OK: {ID}-INIT-V")
        vid.write(INIT.content)
        while True:
            SEG = hotstar.get(video_base_url + f"seg-{c}.m4s", headers=MPD_HEADERS)
            if SEG.status_code == 200:
                print(f"OK: {ID}-{c}V")
                vid.write(SEG.content)
                c += 1
            else:
                break

    with open(f"{ID}-aud.m4s", "wb") as vid:
        c = 1
        INIT = hotstar.get(audio_base_url + "init.mp4", headers=MPD_HEADERS)
        vid.write(INIT.content)
        print(f"OK: {ID}-INIT-A")
        while True:
            SEG = hotstar.get(audio_base_url + f"seg-{c}.m4s", headers=MPD_HEADERS)
            if SEG.status_code == 200:
                print(f"OK: {ID}-{c}A")
                vid.write(SEG.content)
                c += 1
            else:
                break

    subprocess.run(["ffmpeg",
                    "-i", f"{ID}-vid.m4s",
                    "-i", f"{ID}-aud.m4s", 
                    "-map", "0",
                    "-map", "1", 
                    "-c", "copy",
                    f'{ID}.mp4'])
