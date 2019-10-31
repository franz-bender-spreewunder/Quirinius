import os

import numpy as np
from cv2 import cv2

from Quirinius.DifferentialFrame import DifferentialFrame


class FrameSaver:
    def __init__(self):
        self.x = 0
        pass

    def update(self, frame):
        if self.x >= 200:
            frame = np.clip(frame * 40.0, 0,  255)
            im = frame.astype('uint8')
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
            cv2.imwrite('data/' + str(self.x + 19800).zfill(8) + '.png', im)
        self.x += 1
