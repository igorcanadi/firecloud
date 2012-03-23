

import socket
from threading import Thread
from Queue import Queue
from time import sleep
from logger import log

import cPickle as pickle

SLEEP_TIME = 0.01
MAX_SIZE = 3500

class BufSocket(Thread):
  def __init__(self, me):
    super(BufSocket, self).__init__()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.settimeout(.01)
    print 'Bound to :', me
    self.sock.bind(me)
    self.inq = []
    self.outq = []
    self.history = set([])

    self.send_count = 0

  def batch_send(self):
    buckets = {}

    while len(self.outq) > 0:
      (dat, addr) = self.outq.pop()
      if addr not in buckets:
        buckets[addr] = []
      buckets[addr].append(dat)
    self.outq = []

    for addr in buckets.keys():
      d = pickle.dumps(buckets[addr])
      self.sock.sendto(d, addr)
  
  def batch_recv(self):
    while True:
      try:
        d, addr = self.sock.recvfrom(1024 * 8)
      except socket.timeout:
        break
      if d.startswith("GET") or d.startswith("PUT"):
        self.inq.append((d, addr))
      else:
        l = pickle.loads(d)
        for i in l:
          self.inq.append((i, addr))
  
  def sendto(self, dat, addr):
    self.outq.append((dat, addr))
    if len(self.outq) >= 10:
      self.batch_send()

  def __iter__(self):
    return self

  def next(self):
    if len(self.inq) > 0:
      log('Received : ' + str(self.inq[len(self.inq)-1]))
      return self.inq.pop()
    raise StopIteration
