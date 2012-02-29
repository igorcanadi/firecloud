import cPickle as pickle
import socket
from collections import namedtuple

Packet = namedtuple('Packet', ['entry', 'is_master', 'type', 'orig'])

TYPE_ACK = 'A'
TYPE_REJOIN = 'R'
TYPE_PUT = 'P'
TYPE_GET = 'G'

def Network(object):
  def __init__(self, addrs, me, master, dispatch):
    self.master = master
    self.me = me

    self.flood = flood
    flood.network = self

    addrs.remove(me)
    self.addrs = addrs
    self.s = socket.socket(AF_INET, socket.SOCK_DGRAM)
    self.s.bind(me)

  def flood_stream(s):
    pass

  def __flood(self, orig, data):
    for a in filter(lambda x: x != orig, self.addrs):
      self.s.sendto(data, a)

  def flood(self, pkt):
    pkt.orig = self.me
    pkt.is_master = self.master
    data = pickle.dumps(pkt)

    self.__flood(None, data)

  def has_seen(self, pkt):
    return pkt.entry.ts in self.seen

  def see(self, pkt):
    self.seen.add(pkt.entry.ts)

  def dispatch(self, entry, t):
    if t == 'A':
      self.log.recvAck(p)
    elif t == 'P':
      self.log.recvPut(p)
    elif t == 'G':
      self.log.recvGet(p)
    elif t == 'R':
      self.log.recv(p)

  def poll(self):
    while True:
      (data, addr) = self.s.recvfrom()
      pkt = pickle.loads(data)
      if self.has_seen(pkt) continue

      self.see(pkt)
      self.dispatch(pkt.entry, pkt.type)
      self.__flood(addr, data)
