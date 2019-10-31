import sys

import numpy as np
from keras.models import load_model
import keras


class PedestrianCounter:
    def __init__(self):
        self.model = load_model('model.h5', custom_objects={'keras': keras})
        self.buffer = np.zeros((1, 100, 24, 32, 1))
        self.count = 0.0
        self.i = 0

    def update(self, frame):
        expanded = np.expand_dims(frame, axis=2)
        self.buffer[0, 1:] = self.buffer[0, :-1]
        self.buffer[0, 1] = expanded

        self.process(self.buffer)

        self.i += 1

    def process(self, buffer):
        out = np.argmax(self.model.predict(buffer)[0])
        self.count += out / 100.0
        print(self.count, out)
