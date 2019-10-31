
import os

import numpy as np
from cv2 import cv2

image = cv2.imread(
    "/Users/franzbender/Software/Quirinius/data/42/0000000000000045.png",
    cv2.IMREAD_GRAYSCALE
)

bs = image.tobytes()

im2 = np.frombuffer(bs, dtype='uint8')

pass