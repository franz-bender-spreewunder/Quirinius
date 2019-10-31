import glob
import os
import random
from time import time

import cv2
import keras
import numpy as np
from keras import Input, Model
from keras.callbacks import TensorBoard, ModelCheckpoint, Callback
from keras.layers import Dense, Flatten, ConvLSTM2D, BatchNormalization, MaxPooling3D, TimeDistributed, Conv2D, LSTM, \
    Concatenate, Lambda, Add, MaxPooling2D, Dropout
from keras.optimizers import Adam, SGD
from sklearn.utils import class_weight, compute_class_weight

length = 100

########################################################################################################################
#                                                                                                                      #
#                                                Load Data IDs                                                         #
#                                                                                                                      #
########################################################################################################################


cats = next(os.walk('./labeled/'))[1]

data = []
labels = {}

for category in cats:
    items = next(os.walk('./labeled/' + category))[1]
    for item in items:
        p = os.path.join('.', 'labeled', category, item)
        data.append(p)
        labels[p] = int(category)

random.seed(112358)
random.shuffle(data)

out = [labels[x] for x in data]

print("Data Length", len(data))

classWeight = compute_class_weight('balanced', np.unique(out), out)
classWeight = dict(enumerate(classWeight))


########################################################################################################################
#                                                                                                                      #
#                                                Define Generator                                                      #
#                                                                                                                      #
########################################################################################################################


class AugmentedGenerator(keras.utils.Sequence):
    def __init__(self, data, labels, augment, end, start):
        self.data = data[start:end]
        self.labels = labels
        self.augment = augment
        if augment:
            self.indexes = np.arange(len(self.data) * 64)
        else:
            self.indexes = np.arange(len(self.data))
        self.batches = 1
        self.random = random.Random(42)
        self.on_epoch_end()
        self.indexes = self.indexes

    def __load_sequence(self, i):
        if self.augment:
            id = self.data[i >> 6]
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
            shift = (i >> 3) & 3
            brighten = (i >> 5) & 1

            if reverse == 1:
                X = self.__reverse(X)
            X = self.__flip(X, flip)

            if shift > 1:
                X = self.__time_shift(X, shift - 2)

            if shift == 1:
                X = self.__remap_time(X)

            if brighten == 1:
                X = self.__brighten(X)

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
        return len(self.indexes) >> 4


training_generator = AugmentedGenerator(data, labels, augment=True, start=0, end=40)
validation_generator = AugmentedGenerator(data, labels,  augment=False, start=40, end=63)

# Design model
input_tensor = Input(shape=(length, 24, 32, 1))

# c1 = TimeDistributed(Conv2D(filters=4, padding='valid', kernel_size=3))(input_tensor)
# c2 = TimeDistributed(Conv2D(filters=4, padding='valid', kernel_size=3))(c1)
# c3 = TimeDistributed(Conv2D(filters=4, padding='valid', kernel_size=3))(c2)
#
# f1 = TimeDistributed(Flatten())(c3)

c1 = TimeDistributed(Conv2D(filters=4, padding='same', kernel_size=3))(input_tensor)
c2 = TimeDistributed(Conv2D(filters=4, padding='same', kernel_size=3))(c1)
m1 = TimeDistributed(MaxPooling2D(pool_size=(2, 2)))(c2)
r5 = Dropout(0.5)(m1)
c3 = TimeDistributed(Conv2D(filters=8, padding='same', kernel_size=2))(r5)
c4 = TimeDistributed(Conv2D(filters=16, padding='same', kernel_size=2))(c3)
m2 = TimeDistributed(MaxPooling2D(pool_size=(2, 2)))(c4)
r6 = Dropout(0.5)(m2)

f1 = TimeDistributed(Flatten())(r5)

s1 = Lambda(lambda x: keras.backend.sum(x, axis=2, keepdims=True))(f1)

l1 = LSTM(32, return_sequences=True)(f1)
l2 = LSTM(32, return_sequences=True)(l1)
l3 = LSTM(16, return_sequences=True)(l2)
l4 = LSTM(8, return_sequences=True)(l3)
r3 = Dropout(0.5)(l4)
d1 = TimeDistributed(Dense(100, activation='relu'))(r3)

a1 = Concatenate()([d1, s1])
f2 = Flatten()(a1)

r4 = Dropout(0.5)(f2)

d2 = Dense(7, activation='softmax')(r4)

model = Model(input_tensor, d2)
model.summary(line_length=150)

model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

filepath = "model3-{epoch:02d}-{val_loss:.2f}.h5"

checkpoint = ModelCheckpoint(filepath, monitor='val_loss', verbose=1, save_weights_only=False, save_best_only=True,
                             mode='min')

callbacks_list = [checkpoint]
# Train model on dataset
model.fit_generator(generator=training_generator,
                    validation_data=validation_generator,
                    use_multiprocessing=True,
                    workers=8,
                    epochs=100,
                    callbacks=callbacks_list)  # ,
# class_weight=classWeight)

model.save(filepath)

X, y = validation_generator.__getitem__(0)
# X = np.zeros((3, 24, 32, 1))
# X[0,] = np.expand_dims(cv2.imread('./labeled/1565340754.098374-1.0.png', cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
# X[1,] = np.expand_dims(cv2.imread('./labeled/1565340725.230449-1.0.png', cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
# X[2,] = np.expand_dims(cv2.imread('./labeled/1565340699.883803-0.0.png', cv2.IMREAD_GRAYSCALE), axis=2) / 255.0

predictions = model.predict(X)

print(predictions)
