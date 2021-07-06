# Purpose: Extract frames from video

import cv2
import os
import progressbar
import threading


class ExtractFrames:
    def __init__(self, video_path, person_name):
        self.video_path = video_path
        self.person_name = person_name
        if not os.path.isdir(f"Images/Known/{str(person_name)}"):
            os.makedirs(f'Images/Known/{str(person_name)}')

    def extract(self):
        video = cv2.VideoCapture(self.video_path)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"Frame Count: {str(frame_count)}")
        bar = progressbar.ProgressBar(maxval=frame_count,
                                      widgets=[progressbar.Bar('⬛', '[', ']', '⬜'), ' ',
                                               progressbar.Percentage()]).start()

        index = 0
        while video.isOpened():
            ret, frame = video.read()
            if not ret:
                break
            cv2.imwrite(
                f"Images/Known/{self.person_name}/{os.path.basename(self.video_path).split('.')[0] + '_'  + str(index)}.jpg", frame)

            index += 1
            bar.update(bar.currval + 1)
        bar.finish()
        video.release()
        cv2.destroyAllWindows()


# Example
if __name__ == "__main__":
    videos = os.listdir("Videos")
    threads = [ExtractFrames(
        f"Videos/{video}", "Olivia Rodrigo").extract() for video in videos]
    for thread in threads:
        thread.start()
