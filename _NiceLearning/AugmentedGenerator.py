import os
import random

import cv2
import keras
import numpy as np


class AugmentedGenerator(keras.utils.Sequence):
    def __init__(self, data, labels, augment, end, start):
        self.data = data[start:end]
        self.labels = labels
        self.augment = augment
        if augment:
            self.indexes = np.arange(len(self.data) * 8)
        else:
            self.indexes = np.arange(len(self.data))
        self.batches = 1
        self.random = random.Random(42)
        self.on_epoch_end()
        self.indexes = self.indexes

    def __load_sequence(self, i):
        if self.augment:
            id = self.data[i >> 3]
        else:
            id = self.data[i]
        X = np.zeros((100, 24, 32, 1))
        j = 0
        for img in next(os.walk(id))[2]:
            if img[0] == '.':
                continue
            p = os.path.join(id, img)
            X[j] = np.expand_dims(cv2.imread(p, cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
            j += 1
        y = self.labels[id]

        if self.augment:
            reverse = i & 1
            flip = (i >> 1) & 3
            #shift = (i >> 3) & 3
            #brighten = (i >> 5) & 1

            if reverse == 1:
                X = self.__reverse(X)
            X = self.__flip(X, flip)

            #if shift > 1:
            #    X = self.__time_shift(X, shift - 2)

            #if shift == 1:
            #    X = self.__remap_time(X)

            #if brighten == 1:
            #    X = self.__brighten(X)

        return X, y

    def __flip(self, sequence, mode):
        x_flip = mode & 1
        y_flip = mode >> 1

        out = sequence

        if x_flip == 1:
            out = np.flip(out, axis=2)
        if y_flip == 1:
            out = np.flip(out, axis=1)

        return out

    def __time_shift(self, sequence, mode):
        shift = 10
        if mode == 0:
            sequence[shift:, ...] = sequence[:-shift, ...]
            sequence[:shift, ...] = np.zeros((shift, 24, 32, 1))
            return sequence
        else:
            sequence[:-shift, ...] = sequence[shift:, ...]
            sequence[-shift:, ...] = np.zeros((shift, 24, 32, 1))
            return sequence

    def __brighten(self, sequence):
        return sequence * 1.25

    def __remap_time(self, sequence):
        def index(i):
            return int(np.floor(-np.power(np.cos(float(i) / 100.0 * np.pi), 3.0) * 50.0 + 50.0))

        out = np.zeros((100, 24, 32, 1))
        for i in range(100):
            new_i = index(i)
            out[i] = sequence[new_i]
        return out

    def on_epoch_end(self):
        np.random.shuffle(self.indexes)

    def __reverse(self, sequence):
        return np.flip(sequence, axis=0)

    def __getitem__(self, index):
        X = np.zeros((1, 100, 24, 32, 1))
        y = np.zeros((1, 1))
        X[0], y[0] = self.__load_sequence(self.indexes[index])
        return X, y

    def __len__(self):
        return len(self.indexes) >> 3