import yt_dlp

link = input("Enter the YouTube link: ")

ydl_opts = {}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([link])

print("Download complete!")