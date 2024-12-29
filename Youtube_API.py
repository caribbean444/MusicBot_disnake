import urllib.parse as p
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("YOUTUBE_API_KEY")
youtube = build("youtube", "v3", developerKey=api_key)



async def name_video(url):
    if url.startswith('https://youtu.be/'):
        url= url.replace('https://youtu.be/',"")
        o=None
        for i in range(len(url)):
            if url[i]=="?":
                o=i
                break
        for i in range(o+1,len(url)):
            url=url[0:i-1]
        video_id = url
        request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
        response = request.execute()
        return str(response["items"][0]["snippet"]["title"])
    else:
        parsed_url = p.urlparse(url)
        video_id = p.parse_qs(parsed_url.query).get("v")[0]
        request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
        response = request.execute()
        return str(response["items"][0]["snippet"]["title"])

def name_video_no_async(url):
    parsed_url = p.urlparse(url)
    video_id = p.parse_qs(parsed_url.query).get("v")[0]
    request = youtube.videos().list(part="snippet,contentDetails", id=video_id)
    print(url)
    response = request.execute()
    return str(response["items"][0]["snippet"]["title"])
