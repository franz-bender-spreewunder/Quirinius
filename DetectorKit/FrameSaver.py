import os

import numpy as np
from cv2 import cv2


class FrameSaver:
    def __init__(self, folder, prefix, dry_run=200):
        self.dry_run = dry_run
        self.folder = folder
        self.prefix = prefix
        self.x = 0

    def update(self, frame):
        if self.x >= self.dry_run:
            frame = np.clip(frame * 40.0, 0, 255)
            im = frame.astype('uint8')
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
            name = self.prefix + str(self.x - self.dry_run).zfill(16) + '.png'
            path = os.path.join(self.folder, name)
            cv2.imwrite(path, im)
        self.x += 1
