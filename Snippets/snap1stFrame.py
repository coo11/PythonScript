# -*- coding: utf-8 -*-
import os, cv2
from time import time

def getVideos(dir):
    files = os.listdir(dir)
    video_files = [i for i in files if i[-3:].lower() in ['mp4', 'mkv']]
    n = len(video_files)
    if n == 0:
        raise Exception("No required format(s) found.")
    print(f'{n} video(s) found.')
    return video_files
 
def snap_first_frame(work_dir = os.getcwd(), save_dir = os.path.join(os.environ["USERPROFILE"], f"Desktop/Snapshots_{int(time())}")):
    videos = getVideos(work_dir)
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    for i in videos:
        videos_dir = os.path.join(work_dir, i)
        cap = cv2.VideoCapture(videos_dir)
        success, frame = cap.read()
        if success:
            cv2.imwrite(os.path.join(save_dir, f'{i[:-4]}.jpg'), frame)
        cap.release()
    print('Done.')

if __name__ == "__main__":
    path = input("Input dir you wanna batch process:")
    snap_first_frame(path)