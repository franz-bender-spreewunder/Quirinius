import os
from random import random, Random

import keras
import numpy as np
from cv2 import cv2


class AugmentedGenerator(keras.utils.Sequence):
    def __init__(self, data, labels):
        self.data = data
        self.labels = labels
        self.indexes = np.arange(len(self.data) * 8)
        self.batches = 1
        self.random = Random(42)

    def __load_sequence(self, id):
        X = np.zeros((100, 24, 32, 1))
        j = 0
        for img in next(os.walk(id >> 3))[2]:
            if img[0] == '.':
                continue
            p = os.path.join(id, img)
            X[j] = np.expand_dims(cv2.imread(p, cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
            j += 1
        y = self.labels[id]

        reverse = id & 1
        flip = (id >> 1) & 3

        if reverse == 1:
            X = self.__reverse(X)
        X = self.__flip(X, flip)

        return X, y

    def __flip(self, sequence, mode):
        x_flip = mode & 1
        y_flip = mode >> 1

        out = sequence

        if x_flip == 1:
            out = np.flip(out, 2)
        if y_flip == 1:
            out = np.flip(out, 1)

        return out

    def on_epoch_end(self):
        np.random.shuffle(self.indexes)

    def __reverse(self, sequence):
        return np.flip(sequence, 0)

    def __getitem__(self, index):
        X = np.zeros((1, 100, 24, 32, 1))
        X[0], y = self.__load_sequence(self.indexes)
        return X, y

    def __len__(self):
        return len(self.indexes)
