import numpy as np


class RawFrame:
    """
    Represents a raw frame coming from the sensor

    This class also allows you to extract the information stored in the internal data bytes object
    """

    def __init__(self, data: bytes):
        """
        A new RawFrame

        :param data: a bytes-like object of length 3076
        """
        if not data:
            raise ValueError("data can't be empty")
        if len(data) != 3076:
            raise TypeError("data must be of length 3076")
        self.data = data

    def get_time(self) -> int:
        """
        Returns the system time for the frame

        :return: system time of frame in milliseconds since boot
        """
        time_part = self.data[0:4]
        time = int.from_bytes(time_part, byteorder='little', signed=False)
        return time

    def get_image(self) -> np.ndarray:
        """
        Returns the image as a numpy array. The image will still be flattened.

        :return: image as a float32 numpy array of shape=(3072)
        """
        image_part = self.data[4:3076]
        image = np.frombuffer(image_part, np.float32)
        return image.astype(np.float32)
