import errno
import socket
import socketserver
import threading
from typing import Callable

from DetectorKit.DocInherit import doc_inherit
from DetectorKit.RawFrame import RawFrame
from DetectorKit.FrameProvider import FrameProvider


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

        id_raw = self.request.recv(4)
        id = int.from_bytes(id_raw, byteorder='little', signed=False)

        while not self.server.please_shutdown:
            try:
                data = self.request.recv(32)
                total = total + data

                if len(total) > 8 * 768:
                    start = self.strip_for_start(total)
                    self.server.owner.put_frame(id, self.client_address[0], total[start:start + 3076])
                    total = total[3076 + start:]

            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                    continue


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)


class Receiver():
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
        self.providers = []
        self.server_thread = None
        self.server.please_shutdown = False

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
        self.server.please_shutdown = True
        self.server.shutdown()

    def put_frame(self, client_id: int, client_address: str, data: bytes) -> None:
        """
        Accepts a frame received by the StreamHandler
        """
        frame = RawFrame(data)

        for provider in self.providers:
            if provider[0] == client_id:
                provider[1].frame = frame
                provider[1].dirty = True
                provider[1].inform_listeners()

    def get_frame_provider(self, id: int):
        provider = (id, SingleFrameProvider())
        self.providers.append(provider)
        return provider[1]


class SingleFrameProvider(FrameProvider):
    def __init__(self):
        self.dirty = False
        self.frame = None
        self.listeners = []

    def inform_listeners(self):
        for listener in self.listeners:
            listener()

    def is_dirty(self) -> bool:
        return self.dirty

    def get_frame(self) -> RawFrame:
        self.dirty = False
        return self.frame

    @doc_inherit
    def listen_for_updates(self, id: int, listener: Callable[[], None]) -> None:
        self.listeners.append((id, listener))
