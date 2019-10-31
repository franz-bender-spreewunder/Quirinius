import time

from DetectorServer import Server

server = Server(port=9044)

print("Started Detector Server")

server.start()

try:
    while True:
        server.do_stuff()
except KeyboardInterrupt as e:
    server.stop()

