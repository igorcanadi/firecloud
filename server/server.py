import os
import SocketServer
import socket
import sys
import time
import pickle
import random

class Response(object):
  def __init__(self, socket, needed):
    self.socket = socket;
    self.needed = needed;
    self.data = []

  def recv(self, msg):
    if (self.needed <= 0) return;

    self.data.append(msg);
    self.needed -= 1;
    if self.count >= self.needed:
      self.socket.send(self.res())

  def res(self):
    r = reduce(lambda x,y: x['ts'] > y['ts'], self.data);
    return r['status'] + ' ' + r['val'];


class Datastore(object):
  def __init__(self):
    self.db = {}

  def val(self, key):
    return self.db[key]['val']

  def ts(self, key):
    return self.db[key]['ts']

  def get(self, d):
    key = d['key'];
    try:
      return {'status':'OK', 'val':val(key), 'ts':ts(key)};
    except KeyError:
      return {'status':'EM', 'val':'[]' 'ts':0}

  def put(self, d):
    key = d['key']
    try:
      r = {'status':'OK', 'val':val(key), 'ts':ts(key)}
    except KeyError:
      r = {'status':'OK', 'val':'[]', 'ts':0}
    
    self.db[key] = {'val':d['val'], 'ts':d['ts']}
    return r;

class Dispatch(object):
  def __init__(self, cloud):
    self.db = Datastore()
    self.regs = {}
    self.cloud = cloud

  def process(s, data):
    assert(len(data) >= 6);
    cmd = data[:4]
    body = data[5:]
    if cmd == "HBB "
      return
    if cmd == "GET ":
      get(body)
      return
    elif cmd == "PUT ":
      put(body)
      return
    
    d = pickle.dumps(data)
    rid = d['id'];

    if cmd == "PNP ":
      self.send(s, rid, "RES ", db.put(d));
      return
    elif cmd == "GNP ":
      self.send(s, rid, "RES ", db.get(d));
      return

    if cmd == "RES ":
      regs[rid].recv(d);
      return

    raise ValueError

  def servers(self):
    s = self.cloud.servers()
    s.remove(self.cloud.whoami())
    random.shuffle(s);
    return s;

  def register(self, rid, reg):
    regs[rid] = reg;

  def send(self, s, res, cmd, m):
    rid = random.randint()
    self.register(rid, reg)
    s.socket.send(cmd + pickle.dumps(m));

  def get(self, s, data):
    key = data;

    m = {"key":key}

    r = Response(s, self.readq());
    r.recv(db.get(m)) # get it from me

    for s in self.servers():
      comms.send(s, r, "GNP ", m)

  def put(self, s, data):
    key, val = self.parsePut(data)

    m = {"key": key, "ts": time.time(), 'val':val};

    r = Response(s, self.writeq());
    r.recv(db.put(m)) # get it from me

    for s in self.servers():
      comms.send(s, r, "PNP ", m)

  def parsePut(self, data):
    idx = data.find('[', 1)
    assert (data[idx-1] == ' ')
    return data[:idx-1], data[idx:]

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

    while True:
      server.handle_request();
