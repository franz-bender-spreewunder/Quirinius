from abc import ABC, abstractmethod
from typing import Callable

from Quirinius import RawFrame


class FrameProvider(ABC):
    """
    A FrameProvider provides raw frames and informs listeners about new frames
    """

    @abstractmethod
    def is_dirty(self) -> bool:
        """
        Checks whether the currently available frame has already been read or not

        :return: true if a new frame is available, false if frame has already been read
        """

    @abstractmethod
    def get_frame(self) -> RawFrame:
        """
        Gets the newest available frame. Unless a new frame is available always returns the same frame

        :return:  newest available frame
        """
        pass

    @abstractmethod
    def listen_for_updates(self, listener: Callable[[], None]) -> None:
        """
        Registers a listener that gets called when a new frame is available

        :param listener: the listener that gets informed about new frames
        """