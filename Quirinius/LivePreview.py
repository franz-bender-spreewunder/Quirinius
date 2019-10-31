import cv2
import numpy as np


class LivePreview:
    def __init__(self):
        pass

    def update(self, frame):
        frame = np.clip(frame * 400.0, 0, 255)
        im = frame.astype('uint8')
        im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        cv2.imshow('image', im)
        cv2.waitKey(1)