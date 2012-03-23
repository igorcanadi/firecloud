import netlayer
from netlayer import BufSocket
import db

CLIENT = 33
SERVER = 11

class Clock(object):
  def __init__(self):
    self.clock = 0
  def inc(self):
    self.clock += 3
  def get(self):
    return self.clock
  def max(self, other):
    self.clock = max(self.clock, other) + 1

clock = Clock()

class Flooder(object):
  def __init__(self, addrs, me, master):
    self.addrs = addrs
    self.r = BufSocket(me)
    self.me = me
    self.master = int(master)
    self.seen = set()

  def __flood(self, orig, data):
    for a in filter(lambda x: x != orig, self.addrs):
      self.r.sendto(data, a)

  def __filter(self, req, addr):
    try:
      (entry, m, typ, origin, seq, other_clock) = req
      entry = db.Entry._make(entry)
      if (other_clock, origin) in self.seen:
        return None

      self.seen.add( (other_clock, origin) )
      clock.max(other_clock)
      return (SERVER, (entry, m, typ, seq))
    except ValueError:
      return (CLIENT, (req, addr))
  
  def send(self, entry, typ, seq):
    pkt = (tuple(entry), self.master, typ, self.me, seq, clock.get())
    self.__flood(None, pkt)

  def __iter__(self):
    return self

  def next(self):
    req = self.r.recv()
    while req is None:
      self.r.batch_send()
      self.r.batch_recv()
      req = self.r.recv()

    data, origin = req
    val = self.__filter(data, origin)
    if val is not None:
      self.__flood(origin, data)
      return val

