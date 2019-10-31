from keras.layers import Add
from scipy.stats import rankdata
import keras.backend as K


def mar(y_true, y_pred):
    v = 5.0
    number = K.tf.count_nonzero(K.tf.greater_equal(y_pred, v)) - 1.0
    return number


def calculate_mAP(y_true, y_pred):
    average_precisions = []
    relevant = K.sum(K.round(K.clip(y_true, 0, 1)))
    tp_whole = K.round(K.clip(y_true * y_pred, 0, 1))
    for index in range(8):
        temp = K.sum(tp_whole[:, :index + 1], axis=1)
        average_precisions.append(temp * (1 / (index + 1)))
    AP = Add()(average_precisions) / relevant
    mAP = K.mean(AP, axis=0)
    return mAP
