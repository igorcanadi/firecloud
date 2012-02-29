import cPickle as pickle
import socket
from collections import namedtuple

Packet = namedtuple('Packet', ['entry', 'is_master', 'type', 'orig'])

TYPE_REJOIN = 'R'
TYPE_PUT = 'P'
TYPE_PACK = 'A'
TYPE_GET = 'G'
TYPE_GACK = 'H'

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

  def dispatch(self, entry, t, m):
    if t == TYPE_GACK:
      self.db.put(entry)
    elif t == TYPE_GET:
      self.flood(db[entry.key])
    elif t == TYPE_PUT:
      t = Tx(entry)
      self.txs[(entry.ket, entry.tstamp)] = t
      t.ack(self.is_master)
    elif t == TYPE_PACK:
      t = self.txs[(entry.key, entry.tstamp)]
      t.ack(m)

  def poll(self):
    while True:
      (data, addr) = self.s.recvfrom()
      pkt = pickle.loads(data)
      if self.has_seen(pkt) continue

      self.see(pkt)
      self.dispatch(pkt.entry, pkt.type)
      self.__flood(addr, data)
