import glob
import os
import random
from time import time

import cv2
import keras
import numpy as np
from keras import Input, Model
from keras.callbacks import TensorBoard, ModelCheckpoint, Callback
from keras.layers import Dense, Flatten, ConvLSTM2D, BatchNormalization, MaxPooling3D, TimeDistributed
from keras.optimizers import Adam


class DataGenerator(keras.utils.Sequence):
    'Generates data for Keras'

    def __init__(self, list_ids, labels, batch_size=1, dim=(20, 24, 32), n_channels=1, shuffle=True):
        'Initialization'
        self.dim = dim
        self.batch_size = batch_size
        self.labels = labels
        self.list_IDs = list_ids
        self.n_channels = n_channels
        self.shuffle = shuffle
        self.indexes = np.arange(len(self.list_IDs))
        self.on_epoch_end()

    def __len__(self):
        return int(np.floor(len(self.list_IDs) / self.batch_size))

    def __getitem__(self, index):
        # Generate indexes of the batch
        indexes = self.indexes[index * self.batch_size:(index + 1) * self.batch_size]

        # Find list of IDs
        list_ids_temp = [self.list_IDs[k] for k in indexes]

        # Generate data
        X, y = self.__data_generation(list_ids_temp)

        return X, y

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.list_IDs))
        if self.shuffle:
            np.random.shuffle(self.indexes)

    def __data_generation(self, list_ids_temp):
        'Generates data containing batch_size samples'  # X : (n_samples, *dim, n_channels)
        # Initialization
        X = np.empty((self.batch_size, *self.dim, self.n_channels))
        y = np.empty(self.batch_size, dtype=float)

        # Generate data
        for i, ID in enumerate(list_ids_temp):
            j = 0
            for img in next(os.walk(ID))[2]:
                if img[0] == '.':
                    continue
                p = os.path.join(ID, img)
                X[i, j,] = np.expand_dims(cv2.imread(p, cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
                j += 1
            y[i] = self.labels[ID]

        return X, y


cats = next(os.walk('./labeled/'))[1]

data = []
labels = {}

for category in cats:
    items = next(os.walk('./labeled/' + category))[1]
    for item in items:
        p = os.path.join('.', 'labeled', category, item)
        data.append(p)
        labels[p] = float(category)

random.seed(42)
random.shuffle(data)

# Generators
training_generator = DataGenerator(data[:-10], labels)
validation_generator = DataGenerator(data[-10:], labels)

# Design model
inpTensor = Input(shape=(20, 24, 32, 1))

c1 = ConvLSTM2D(filters=8, kernel_size=(5, 5), padding='same', data_format='channels_last',
                recurrent_activation='sigmoid'
                , activation='sigmoid', return_sequences=True)(inpTensor)
n1 = BatchNormalization()(c1)
p1 = MaxPooling3D(pool_size=(1, 2, 2), padding='same', data_format='channels_last')(n1)

c2 = ConvLSTM2D(filters=4, kernel_size=(2, 2), padding='same', data_format='channels_last',
                recurrent_activation='sigmoid'
                , activation='sigmoid', return_sequences=True)(p1)
n2 = BatchNormalization()(c2)
p2 = MaxPooling3D(pool_size=(1, 2, 2), padding='same', data_format='channels_last')(n2)

f1 = TimeDistributed(Flatten())(p2)
d1 = TimeDistributed(Dense(48))(f1)
d2 = TimeDistributed(Dense(10))(d1)

f2 = Flatten()(d1)
d3 = Dense(units=100, activation='sigmoid')(f2)
d4 = Dense(units=10, activation='sigmoid')(d3)
d5 = Dense(units=1, activation='sigmoid')(d4)

model = Model(inpTensor, d5)

model.compile(loss='mean_squared_logarithmic_error', optimizer='adam', metrics=['accuracy'])

tensorboard = TensorBoard(log_dir="logs/{}".format(time()))

filepath = "weights.best.h5"

callbacks_list = [tensorboard]
# Train model on dataset
model.fit_generator(generator=training_generator,
                    validation_data=validation_generator,
                    use_multiprocessing=True,
                    workers=8,
                    epochs=50,
                    callbacks=callbacks_list)

model.save(filepath)

X, y = validation_generator.__getitem__(0)
# X = np.zeros((3, 24, 32, 1))
# X[0,] = np.expand_dims(cv2.imread('./labeled/1565340754.098374-1.0.png', cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
# X[1,] = np.expand_dims(cv2.imread('./labeled/1565340725.230449-1.0.png', cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
# X[2,] = np.expand_dims(cv2.imread('./labeled/1565340699.883803-0.0.png', cv2.IMREAD_GRAYSCALE), axis=2) / 255.0

predictions = model.predict(X)

print(predictions)
