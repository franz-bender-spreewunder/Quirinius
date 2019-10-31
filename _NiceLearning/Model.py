import keras
from keras import Input, Model
from keras.layers import Dense, Flatten, TimeDistributed, Conv2D, LSTM, Concatenate, Lambda, MaxPooling2D, Dropout


class ModelGenerator:
    @staticmethod
    def generate_model():
        input_tensor = Input(shape=(100, 24, 32, 1))

        c1 = TimeDistributed(Conv2D(filters=4, padding='same', kernel_size=3))(input_tensor)
        c2 = TimeDistributed(Conv2D(filters=4, padding='same', kernel_size=3))(c1)
        r5 = Dropout(0.5)(c2)
        c3 = TimeDistributed(Conv2D(filters=8, padding='same', kernel_size=2))(r5)
        c4 = TimeDistributed(Conv2D(filters=8, padding='same', kernel_size=2))(c3)
        r6 = Dropout(0.5)(c4)

        f1 = TimeDistributed(Flatten())(r6)
        d3 = TimeDistributed(Dense(100, activation='relu'))(f1)

        s1 = Lambda(lambda x: keras.backend.sum(x, axis=2, keepdims=True))(d3)

        l1 = LSTM(32, return_sequences=True)(f1)
        l2 = LSTM(32, return_sequences=True)(l1)
        l3 = LSTM(16, return_sequences=True)(l2)
        l4 = LSTM(8, return_sequences=True)(l3)
        r3 = Dropout(0.5)(l4)
        d1 = TimeDistributed(Dense(100, activation='relu'))(r3)

        a1 = Concatenate()([d1, s1])
        f2 = Flatten()(a1)

        r4 = Dropout(0.5)(f2)

        d2 = Dense(8, activation='softmax')(r4)

        model = Model(input_tensor, d2)
        return model
