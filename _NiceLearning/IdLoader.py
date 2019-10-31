import os
import random

import numpy as np
from sklearn.utils import compute_class_weight


class IdLoader:
    @staticmethod
    def load_ids():
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

        return data, labels, classWeight