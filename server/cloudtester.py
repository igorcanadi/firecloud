import os
import SocketServer
import socket
import sys
import time
import pickle

class RTCPHandler(SocketServer.BaseRequestHandler):
    def res(tup):
      return ' '.join(tup)

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(8000).strip()
        return

    def handle_timeout(self):
      return

if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])
    print PORT
    server = SocketServer.TCPServer((HOST, PORT), RTCPHandler)
    server.timeout = None

    while True:
      server.handle_request();
