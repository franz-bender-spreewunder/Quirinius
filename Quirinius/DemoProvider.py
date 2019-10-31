import os
import time

from cv2 import cv2


class DemoProvider:
    def __init__(self):
        paths = sorted(next(os.walk('./backup2/'))[2])
        self.images = [cv2.imread(
            os.path.join('./backup2/', x),
            cv2.IMREAD_GRAYSCALE
        ) / 255 for x in paths if x[0] is not '.']
        self.i = 0

    def get_frame(self):
        time.sleep(0.08)
        self.i += 1
        if self.i >= 100: #len(self.images):
            self.i = 0
        return self.images[self.i]
