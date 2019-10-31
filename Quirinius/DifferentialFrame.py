import numpy as np


class DifferentialFrame:
    """
    Represents a preprocessed frame
    """

    def __init__(self, data: np.ndarray):
        """
        A new DifferentialFrame

        :param data: a numpy array in the shape of (24, 32)
        """
        self.data = data

    def get_frame(self) -> np.ndarray:
        return self.data
