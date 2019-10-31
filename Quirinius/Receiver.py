import errno
import socket
import socketserver
import threading
from typing import Callable

from Quirinius.DocInherit import doc_inherit
from Quirinius.RawFrame import RawFrame
from Quirinius.FrameProvider import FrameProvider


class StreamHandler(socketserver.BaseRequestHandler):
    """
    A handler that implements sensor packet detection
    """

    @staticmethod
    def strip_for_start(data):
        """
        Looks for the marker 0x00FFFF00 in the data and returns the position right next to the markers end

        :param data: data that shall be checked
        :return: the position of the new packet (the marker is not part of the packet data)
        """
        pattern = [0, 255, 255, 0]

        for i in range(len(data) - len(pattern)):
            found = True
            for j in range(len(pattern)):
                if data[i + j] != pattern[j]:
                    found = False
                    break
            if found:
                return i + len(pattern)
        return False

    def handle(self):
        """
        Handles an incoming data stream and informs the provider about new packets
        """
        total = bytes()
        self.request.setblocking(True)

        while True:
            try:
                data = self.request.recv(32)
                total = total + data

                if len(total) > 8 * 768:
                    start = self.strip_for_start(total)
                    self.server.owner.put_frame(self.client_address[0], total[start:start + 3076])
                    total = total[3076 + start:]

            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    continue


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class Receiver(FrameProvider):
    """
    Implements a FrameProvider that receives sensor data via TCP
    """

    def __init__(self, host="0.0.0.0", port=35813):
        """
        A new Receiver
        :param host: defines where the server shalll listen (default: accept all connections)
        :param port: defines on which port the server shall listen
        """
        self.server = ThreadedTCPServer((host, port), StreamHandler)
        self.server.owner = self
        self.dirty = False
        self.frame = None
        self.listeners = []
        self.server_thread = None

    def start(self) -> None:
        """
        Start the server

        The server will run in its own thread
        """
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self) -> None:
        """
        Stops the server

        Please not that you can NOT start the server again
        """
        self.server.shutdown()

    def put_frame(self, client_address: str, data: bytes) -> None:
        """
        Accepts a frame received by the StreamHandler
        """
        self.frame = RawFrame(data)
        self.dirty = True
        for listener in self.listeners:
            listener()

    @doc_inherit
    def is_dirty(self) -> bool:
        return self.dirty

    @doc_inherit
    def get_frame(self) -> RawFrame:
        self.dirty = False
        return self.frame

    @doc_inherit
    def listen_for_updates(self, listener: Callable[[], None]) -> None:
        self.listeners.append(listener)
