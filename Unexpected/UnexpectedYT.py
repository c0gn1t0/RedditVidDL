# Program to Crawl, Download, Compile, Add Endscreen and Upload to YouTube Top Videos from Reddit

# Thursday

import os
import praw
import pandas as pd
import requests, os
import subprocess
import datetime
import pytz
from urllib.parse import urljoin
from moviepy.editor import *
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta

# Specify working directory
os.chdir(r"C:\Users\yashi\Videos\RedditVidDL\Unexpected\\")

# Define the folder containing the videos
folder_path = r"C:\Users\yashi\Videos\RedditVidDL\Unexpected\\"

# Get today's date in the format day-month-year
date_str = datetime.now().strftime("%d-%m-%y")

# Python Reddit API Wrapper (PRAW) to connect to the Reddit API and access the top 10 videos on the "videos" subreddit for the past week
reddit = praw.Reddit(
    client_id="XX",
    client_secret="YY",
    user_agent="RedVidDL 1.0 by /u/yprojekt",
)

# Choose subreddit to crawl
subreddit = reddit.subreddit("unexpected")

# Choose how to sort videos and how many to download
# top_videos = subreddit.top(limit=3)
top_videos = subreddit.top("week", limit=20)

titles = []
urls = []

for video in top_videos:
    if video.is_video and "v.redd.it" in video.url and not video.over_18:
        titles.append(video.title)
        urls.append(video.url)
        full_url = urljoin("https://www.reddit.com", video.permalink)
        json_url = full_url[:-1] + ".json"
        r = requests.get(
            json_url,
            headers={
                "User-agent": "Mozilla/5.0 (Macintosh; Intel Mac OSy X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
            },
        )
        data = r.json()[0]
        title = data["data"]["children"][0]["data"]["title"]
        title = "".join(c for c in title if c.isalnum() or c in "._- ")
        title = title.replace(" ", "_")
        video_url = data["data"]["children"][0]["data"]["secure_media"]["reddit_video"][
            "fallback_url"
        ]
        audio_url = "https://v.redd.it/" + video_url.split("/")[3] + "/DASH_audio.mp4"
        with open("video.mp4", "wb") as f:
            g = requests.get(video_url, stream=True)
            f.write(g.content)
        with open("audio.mp3", "wb") as f:
            g = requests.get(audio_url, stream=True)
            f.write(g.content)
        # To add current time so that file names are not same
        now_vid = datetime.now()
        time_str = now_vid.strftime("%H-%M-%S")
        output_filename = f"{title}_{time_str}.mp4"
        os.system(
            f'ffmpeg -i video.mp4 -i audio.mp3 -vf scale=-2:1080 -c:v libx264 -c:a aac -strict experimental -b:a 192k -shortest "{output_filename}"'
        )
        os.remove("video.mp4")
        os.remove("audio.mp3")
        print(full_url)

# Get a list of all the video files in the folder
video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]

# Loop through each video file and check if file has video frames
for file in video_files:
    # Check if file has video stream
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_streams",
            "-select_streams",
            "v",
            os.path.join(folder_path, file),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Check if ffprobe returned any error messages or if the video stream is missing
    if result.stderr or not result.stdout:
        # Delete the file if it is corrupt or does not have a video stream
        os.remove(os.path.join(folder_path, file))
    else:
        # File has video stream
        pass


# Get a list of all the video files in the folder
video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]

# Define the target width and height
target_width = 1920
target_height = 1080

# Create a text file containing a list of all the video files
with open("files.txt", "w") as f:
    for file in video_files:
        f.write(f"file '{os.path.join(folder_path, file)}'\n")
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height",
                "-of",
                "csv=p=0",
                file,
            ],
            stdout=subprocess.PIPE,
        )

        # Parse the output to get the width and height values
        width, height = map(int, result.stdout.decode().strip().split(","))

        # Use ffprobe to check if the video has an audio track
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "a:0",
                "-show_streams",
                "-of",
                "csv=p=0",
                file,
            ],
            stdout=subprocess.PIPE,
        )

        # If there is no audio track in the file, add a silent audio track
        if not result.stdout:
            subprocess.call(
                f'ffmpeg -i {file} -f lavfi -i anullsrc=channel_layout=stereo:sample_rate=44100 -c:v copy -c:a aac -shortest "{file}_silent.mp4"',
                shell=True,
            )
            os.remove(file)
            file = f"{file}_silent.mp4"

        # Calculate the total amount of padding required
        padding_total = target_width - width

        # Calculate the amount of padding to add to each side
        padding_left = padding_total // 2
        padding_right = padding_total - padding_left

        # Add the padding
        subprocess.call(
            f'ffmpeg -i "{file}" -vf "pad={target_width}:{target_height}:{padding_left}:{0}:black" -c:a copy "{file}_padded.mp4"',
            shell=True,
        )
        os.remove(file)

# Get a list of all the video files in the folder
video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]

# Loop through each video file and check if file has video frames
for file in video_files:
    file_path = os.path.join(folder_path, file)
    if os.path.getsize(file_path) == 0:
        os.remove(file_path)
        print(f"{file} deleted because file size is 0 bytes.")
        continue
    else:
        pass

# Get a list of all the video files in the folder
video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]

# Create a text file containing a list of all the video files
with open("files.txt", "w") as f:
    for file in video_files:
        f.write(f"file '{os.path.join(folder_path, file)}'\n")

# Create a list of all the video clips
video_clips = [VideoFileClip(os.path.join(folder_path, file)) for file in video_files]

# Concatenate the video clips
final_clip = concatenate_videoclips(video_clips)

# Write the final video to a file
final_clip.write_videofile(os.path.join(folder_path, "Compilation_NoEndscreen.mp4"))

noscreen_file = f"Compilation_NoEndscreen.mp4"

# Add YouTube Endscreen
endscreen = "C:/Users/yashi/Documents/yProjekt/Media/yProjekt Endscreen 2.mp4"
subprocess.call(
    f'ffmpeg -i {noscreen_file} -i "{endscreen}" -filter_complex "[0:v]scale=1920:-2,setsar=1[v0];[1:v]scale=1920:-2,setsar=1[v1];[v0][0:a][v1][1:a]concat=n=2:v=1:a=1[v][a]" -map "[v]" -map "[a]" -movflags +faststart "Compilation_{date_str}.mp4"',
    shell=True,
)
# Delete the temporary text file
os.remove("files.txt")
os.remove(noscreen_file)

# Setup paths for token and credential files
token_path = (
    "C:\\Users\\yashi\\Videos\\RedditVidDL\\YoutubeAPI Credentials\\token_yp.json"
)
creds_path = (
    "C:\\Users\\yashi\\Videos\\RedditVidDL\\YoutubeAPI Credentials\\credentials_yp.json"
)

# Set up YouTube API client
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
creds = None
if os.path.exists(token_path):
    creds = Credentials.from_authorized_user_file(token_path, SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
        creds = flow.run_local_server(port=0)
    with open(token_path, "w") as token:
        token.write(creds.to_json())
youtube = build("youtube", "v3", credentials=creds)

# Set the title of the uploaded video
title = (
    "Unexpected Compilation | Reddit's Best Videos the Week | "
    + datetime.now().strftime("%d-%m-%y")
)

date_str = datetime.now().strftime("%d-%m-%y")
output_file_name = f"Compilation_{date_str}.mp4"

# get current date and time in "Asia/Kolkata" timezone
now = datetime.now(pytz.timezone("Asia/Kolkata"))

# if today is Thursday, set publish_time to 7 pm today
if now.weekday() == 3:  # 3 represents Thursday
    publish_time = now.replace(hour=19, minute=0, second=0, microsecond=0)
else:
    # otherwise, set publish_time to 7 pm on the next Thursday
    days_until_next_thursday = (3 - now.weekday() + 7) % 7
    next_thursday = now + timedelta(days=days_until_next_thursday)
    publish_time = next_thursday.replace(hour=19, minute=0, second=0, microsecond=0)

# convert publish_time to "Asia/Kolkata" timezone
publish_time = publish_time.astimezone(pytz.timezone("Asia/Kolkata"))

# format publish_time as ISO 8601 string with seconds precision
publish_time_str = publish_time.isoformat(timespec="seconds")

# Set the ID of the playlist to which the video will be added
playlist_id = "PLMmz4EtTgYnLJHyf17dMhrFReoDCGquio"

# Upload the video as a draft to YouTube
try:
    body = {
        "snippet": {
            "title": title,
            "description": "Welcome to the latest edition of our Unexpected Compilation series, where we bring you the best and most surprising moments from around the world.\n\nIn this week's video, you'll see a hilarious mix of unexpected events, heartwarming reactions, and amazing feats that are sure to leave you amazed and entertained. This compilation has something for everyone. Whether you're a fan of viral videos, unexpected endings, or just looking for a good laugh, you won't want to miss this week's roundup.\n\nSo sit back, relax, and enjoy the show! Don't forget to like, comment, and subscribe to our channel for more exciting videos like this one.\n\n👾 | Twitch | https://www.twitch.tv/yprojekt\n📝 | Requests | https://forms.gle/Vo9Hdm9YEd8Lor6u8\n🚀 | Collaborate | Want to get featured / involved with our broadcast? | https://linktr.ee/yprojekt \n📧 | Contact | All rights belong to their respective owners. If any rights owner is ​​not satisfied, let us know at yprojekt@outlook.com\n\n🎧 Thanks for Tuning In 💜\n© 2023 Y Projekt. All rights reserved.\n\n#reddit #unexpected #videos #compilation #funny #viral #entertainment #trending #popular #amazing #awesome #surprising #shocking #crazy #mindblowing #top #bestofreddit #internetfun #youtube #memes #tiktok #funnyvideos #laugh #funnymoments #comedy #contentcreator #fails #jokes #clips #socialmedia",
            "tags": ["unexpected", "compilation", "videos", "reddit", "surprising"],
            "categoryId": "23",
        },
        "status": {
            "privacyStatus": "private",
            "publishAt": publish_time_str,
            "selfDeclaredMadeForKids": False,
        },
        "playlistId": playlist_id,
    }
    youtube.videos().insert(
        part="snippet,status", body=body, media_body=output_file_name
    ).execute()
    print(f"Video {output_file_name} has been uploaded as a draft to YouTube.")
    try:
        os.remove(output_file_name)
        video_files = [f for f in os.listdir(folder_path) if f.endswith(".mp4")]
        for file in video_files:
            os.remove(os.path.join(folder_path, file))
        print(f"Video files hava been deleted from your computer.")
    except OSError as e:
        print(
            f"An error occurred while deleting the video file from your computer: {e.strerror}"
        )
except HttpError as e:
    print(f"An error occurred: {e}")
