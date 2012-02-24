import os
import SocketServer
import socket
import sys
import time
import pickle


class Datastore(object):
  def __init__(self):
    self.d = {}

  def process(data):
    assert(len(data) >= 6);
    cmd = data[:4]
    body = data[5:]
    if cmd == "GET ":
      return get(body)
    elif cmd == "PUT ":
      return put(body)
    elif cmd == "PNP ":
      return pnp(body)
    else:
      raise ValueError

  def get(data):
    try:
      return ("OK", d[data][1]);
    except KeyError:
      return ("EM", "[]");

  def propogate(data):
    for s in cloud.servers():
      s.send("PNP " + pickle.dumps(data));

  def pnp(data):
    t = pickle.loads(data)
    d[t[0]] = t[1]

  def put(data):
    idx = data.find('[', 1)
    assert (data[idx-1] == ' ')
    res = {"key":data[:idx-1], "val":data[idx:], "time":time.time()};

    try:
      ret = ("OK", d[);
    except KeyError:
      ret = ("EM", "[]")

    propogate(key, (time.time(), val))

    return ret


class RTCPHandler(SocketServer.BaseRequestHandler):
    def res(tup):
      return ' '.join(tup)

    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(8000).strip()
        res = process(data);
        if res == None:
          return
        self.request.sendall(res)
    def handle_timeout(self):
      return

if __name__ == "__main__":
    HOST, PORT = "localhost", int(sys.argv[1])
    print PORT
    server = SocketServer.TCPServer((HOST, PORT), RTCPHandler)
    server.timeout = None

    global cloud;
    cloud = Cloud([("localhost", 9998), ("localhost", 9999)], sys.argv[1])

    while True:
      server.handle_request();
      if (int(time.time()) % 3 == 0):
        cloud.hb()
