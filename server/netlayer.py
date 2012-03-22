

import socket
from threading import Thread
from Queue import Queue
from time import sleep
from logger import log

import cPickle as pickle

SLEEP_TIME = 0.01

class BufSocket(Thread):
  def __init__(self, me):
    super(BufSocket, self).__init__()
    self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.sock.setblocking(0)
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
        self.inq.put(l)
        log('Recieved from client: ' + l)
        sleep (SLEEP_TIME)
        continue

      log('Didn\'t put.')
      for i in l:
        self.inq.put(i)
        log('Queued a recieved packet')
      sleep (SLEEP_TIME)
  
  def batch_send(self):
    buckets = {}

    while len(outq) > 0:
      (dat, addr) = self.outq.poll()
      if addr not in buckets:
        buckets[addr] = []
      buckets[addr].append(dat)
      log('Spooled data.')

    for addr in buckets.keys():
      d = pickle.dumps(buckets[addr])
      self.sock.sendto(d, addr)
      log('Sent to: '+ addr)
  
  def batch_recv(self):
    while True:
      try:
        d, addr = self.sock.recvfrom(1024 * 8)
      except socket.error:
        break

      log('Got something!')
      try:
        log('about to un-pickle')
        log('Pickle loads: ' + d)
        l = pickle.loads(d)
        log('Got L:', l)
      except:
        log('About t put.')
        self.inq.append(l)
        log('Recieved from client: ' + l)
        continue

      log('Didn\'t put.')
      for i in l:
        self.inq.put(i)
        log('Queued a recieved packet')
  
  def sendto(self, dat, (host, port)):
    log('Net Send')
    self.outq.append(dat, (host, port))

  def recvfrom(self):
    log('Net recv')
    if len(self.inq) > 0:
      return self.inq.poll()
    return (None, None)
