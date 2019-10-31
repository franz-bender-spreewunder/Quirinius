import os

import keras
import numpy as np
from cv2 import cv2
from keras.engine.saving import load_model

model = load_model('model.h5', custom_objects={'keras': keras})

cats = next(os.walk('./labeled/'))[1]

xxx = 0
off = 0

for category in cats:
    items = next(os.walk('./labeled/' + category))[1]
    for item in items:
        p = os.path.join('.', 'labeled', category, item)
        c = int(category)
        i = 0
        sequence = np.zeros((1, 100, 24, 32, 1))
        for img in next(os.walk(p))[2]:
            p2 = os.path.join(p, img)
            if img[0] != '.':
                sequence[0, i] = np.expand_dims(cv2.imread(p2, cv2.IMREAD_GRAYSCALE), axis=2) / 255.0
                i += 1
        print('----------------------------------------------------------------------------------------------------------------------------------')
        print(f'Testsituation {item}')
        pred = model.predict(sequence)[0]
        for x in range(7):
            print(f'Wahrscheinlichkeit für {x}: ', end='')
            for y in range(int(pred[x] * 100)):
                print('#', end='')
            print('')
        out = np.argmax(pred)
        d = abs(out - c)
        if d > 0:
            xxx += 1
        off += d
        print(f'Abweichung vom korrekten Wert ({c}) ist {d}')

print(f'\n\nAnzahl an Samples, die nicht korrekt waren ist {xxx}')
print(f'Der durchschnittliche Fehler liegt damit bei {off / 64}')