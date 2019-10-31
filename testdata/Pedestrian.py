import os
import uuid

import cv2 as cv
import numpy as np
import scipy
import scipy.stats
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from testdata.Perlin import generate_perlin_noise_2d


class Pedestrian:
    def __init__(self, angle=0.3, duration=0.5):
        self.duration = np.random.random() * 0.2 + 0.3
        self.duration = duration
        self.start = np.random.random() * 0.6 + 0.2
        self.end = self.start + (np.random.random() - 0.5) * angle
        self.noise_x = generate_perlin_noise_2d((100, 1), (4, 1))
        self.noise_y = generate_perlin_noise_2d((100, 1), (2, 1))
        self.offset = np.random.random() * (1.0 - duration)
        self.width = 32
        self.height = 24
        self.length = 100
        self.up = False
        self.intensity = np.random.random() * 0.4 + 0.8
        self.size = np.random.random() * 0.4 + 0.6
        if np.random.random() < 0.5:
            self.up = True

    def get_position(self, frame):
        frame = frame / self.length
        d = np.clip((frame - self.offset) / self.duration, 0.0, 1.0)
        pos_x = (self.start + (self.end - self.start) * d) * self.width

        if self.up:
            pos_y = (d * 1.2 - 0.1) * self.height
        else:
            pos_y = (1.1 - d * 1.2) * self.height

        window_x = scipy.stats.norm(pos_x + self.noise_x[int(frame * 100), 0] * 5.0, self.size)
        window_y = scipy.stats.norm(pos_y + self.noise_y[int(frame * 100), 0] * 3.0, self.size)

        image = np.zeros((24, 32))
        for y in range(24):
            for x in range(32):
                norm_x = x / self.width - 0.5
                norm_y = y / self.height - 0.5

                r_x = norm_x / (0.7 + np.linalg.norm((norm_x, norm_y)))
                r_y = norm_y / (0.7 + np.linalg.norm((norm_x, norm_y)))

                r_x = (r_x + 0.5) * self.width
                r_y = (r_y + 0.5) * self.height

                v = window_x.pdf(r_x) * window_y.pdf(r_y) * 5.0 * self.intensity
                image[y, x] = v

        return image

    def distort(self, x, y):
        return np.linalg.norm((x, y)) / (np.add((1.0, 1.0), np.linalg.norm((x, y))))


p = "./data/"

if not os.path.exists(p):
    os.makedirs(p)

for count in range(4, 8):
    c_path = os.path.join(p, str(count) + '/')
    if not os.path.exists(c_path):
        os.makedirs(c_path)

    for example in range(20):
        folder = str(uuid.uuid1())
        e_path = os.path.join(c_path, folder + '/')
        os.makedirs(e_path)

        p_list = [Pedestrian() for x in range(count)]

        for i in range(100):
            f_list = [p.get_position(i) for p in p_list]
            f_list.append(np.zeros((24, 32)))
            f = np.sum(f_list, axis=0)
            f = np.clip(f*255, 0, 255).astype(np.uint8)
            im = cv.cvtColor(f, cv.COLOR_GRAY2BGR)

            cv.imwrite(os.path.join(e_path, f'{i}.png'), im)

# fig = plt.figure()
# a = np.zeros((24, 32))
# im = plt.imshow(a, interpolation='none')
# p1 = Pedestrian()
# p2 = Pedestrian()
# p3 = Pedestrian()
#
#
# def init():
#     return [im]
#
#
# def update(frame):
#     i1 = p1.get_position(frame) + p2.get_position(frame) + p3.get_position(frame)
#     im.set_data(i1)
#     return [im]
#
#
# ani = FuncAnimation(fig, update, interval=50, frames=np.arange(100), init_func=init, blit=True)
# plt.show()
