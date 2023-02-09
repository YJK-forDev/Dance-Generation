# pip install pytube
# pip install moviepy
# sudo pip3 install imageio==2.4.1
# imageio ext 파일 필요하다는 에러 뜨는 경우, 메시지에 적힌대로 명령어 한 줄 실행할 것
# video 폴더 내에 오디오 없이 추출된 비디오 파일 다운 되어있음
# 사용방법 : 해당 py 파일 실행 후, Enter link 지시어가 뜨면 그 뒤에 원하는 유튜브 링크를 적는다. (ex. Enter link : https://youtu.be/YSY1rVgGhAs)
# 2180 영상은 주로 webm 파일로 제공되는 경우가 많음

from pytube import Playlist, YouTube

from moviepy.editor import *
import ffmpeg

fpath = lambda x: './' + x

def ydown(url: str, prefix: str = ""):
 
    yt = YouTube(url)

    

    vpath = (
        yt.streams.filter(adaptive=True, only_video=True)
        .order_by("resolution")
        .desc()
        .first()
        .download(output_path=fpath("video/"), filename_prefix=f"{prefix} ")
    )
    apath = (
        yt.streams.filter(adaptive=True, file_extension="mp4", only_audio=True)
        .order_by("abr")
        .desc()
        .first()
        .download(output_path=fpath("audio/"), filename_prefix=f"{prefix} ")
    )

    v = VideoFileClip(vpath)
    a = AudioFileClip(apath)

    v.audio = a
    
    v.write_videofile(fpath(f"1080/{vpath.split('/')[-1]}"))
    
    
    

def playlistdown(url: str, prefix: str = ""):
    for i in [url]:
        try:
            ydown(i, prefix)
            
        except:
            continue

url_video = input("Enter link : ")
playlistdown(url=url_video)