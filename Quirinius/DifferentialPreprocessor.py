from typing import Optional

import cv2
import numpy as np

from Quirinius.DifferentialFrame import DifferentialFrame
from Quirinius.RawFrame import RawFrame


class DifferentialPreprocessor:
    def __init__(self):
        self.previous_frame = None
        self.background_matte = None
        self.images_processed = 0
        self.erosion_size = 2

    def process_frame(self, frame: RawFrame) -> Optional[DifferentialFrame]:
        self.images_processed += 1

        if self.previous_frame is None:
            image = frame.get_image()
            self.background_matte = image
            self.previous_frame = np.zeros_like(image).reshape((24, 32))
            return None
        else:
            image = frame.get_image()
            #cv2.imshow('raw', (image.reshape((24, 32)) - 30.0) / 10.0)
            self.update_background_matte(image)
            difference = self.subtract_background(image).reshape((24, 32))
            cleaned = self.noise_and_blur_reduction(difference)
            #flow = self.calculate_optical_flow(cleaned)
            self.previous_frame = self.previous_frame
            return cleaned

    def update_background_matte(self, frame: np.ndarray):
        alpha = 0.005
        inverse_alpha = 1.0 - alpha
        self.background_matte = self.background_matte * inverse_alpha + frame * alpha

    def subtract_background(self, frame: np.ndarray):
        difference = np.abs(frame - self.background_matte)
        return difference

    def noise_and_blur_reduction(self, frame: np.ndarray):
        frame = np.maximum(frame - 0.5, 0)
        frame = np.power(frame, 2.0)

        element = np.array(([0.0, 0.125, 0.0], [0.125, 0.5, 0.125], [0.0, 0.125, 0.0]))
        frame = cv2.filter2D(frame, -1, element)

        element = cv2.getStructuringElement(cv2.MORPH_RECT, (self.erosion_size, self.erosion_size))
        frame = cv2.erode(frame, element)

        return frame

    def calculate_optical_flow(self, frame: np.ndarray):
        flow = cv2.calcOpticalFlowFarneback(prev=self.previous_frame * 250,
                                            next=frame * 250,
                                            flow=None,
                                            pyr_scale=0.5,
                                            levels=3,
                                            winsize=5,
                                            iterations=2,
                                            poly_n=5,
                                            poly_sigma=1.3,
                                            flags=0)

        up = np.zeros_like(flow)
        up[..., 1] = 1.0
        product = np.einsum('ijk,ijk->ij', up, flow)
        product = np.sign(product) * np.maximum(0.0, np.abs(product) - 1.0) / 2.0
        product = np.clip(product, -1.0, 1.0) / 2.0 + 0.5
        return product
