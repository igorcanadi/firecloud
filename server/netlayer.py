

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

  def run(self):
    while True:
      buckets = {}

      while not self.outq.empty():
        (dat, addr) = self.outq.get()
        if addr not in buckets:
          buckets[addr] = []
        buckets[addr].append(dat)
        log('Spooled data.')

      for addr in buckets.keys():
        d = pickle.dumps(buckets[addr])
        self.sock.sendto(d, addr)
        log('Sent to: '+ addr)

      try:
        d, addr = self.sock.recvfrom(1024 * 8)
      except socket.error:
        sleep (SLEEP_TIME)
        continue

      log('Got something!')

      try:
        log('about to un-pickle')
        log('Pickle loads: ' + d)
        l = pickle.loads(d)
        log('Got L:', l)
      except:
        log('About t put.')
        self.inq.put((d, addr))
        log('Recieved from client: ' + d)
        sleep (SLEEP_TIME)
        continue

      log('Didn\'t put.')
      for i in l:
        self.inq.put((i, addr))
        log('Queued a recieved packet')
      sleep (SLEEP_TIME)
  
  def batch_send(self):
    buckets = {}

    while len(self.outq) > 0:
      (dat, addr) = self.outq.pop()
      if addr not in buckets:
        buckets[addr] = []
      buckets[addr].append(dat)
      log('Spooled data.')

    for addr in buckets.keys():
      d = pickle.dumps(buckets[addr])
      self.sock.sendto(d, addr)
      log('Sent to: '+ str(addr))
  
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
    log('Net Send')
    self.outq.append((dat, addr))
    if len(self.outq) >= 10:
      self.batch_send()

  def __iter__(self):
    return self

  def next(self):
    if len(self.inq) > 0:
      return self.inq.pop()
    raise StopIteration
