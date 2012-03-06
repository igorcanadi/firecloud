import cPickle as pickle
import socket
from collections import namedtuple
import tx
import re
import db
import time

Packet = namedtuple('Packet', ['entry', 'is_master', 'type', 'orig'])

TYPE_PUT = 'P'
TYPE_PACK = 'A'
TYPE_GET = 'G'
TYPE_GACK = 'H'

def check(txs):
  while True:
    keys = txs.keys()
    for key in keys:
      t = txs[key]
      if t.state == tx.DEAD:
        del txs[key]
      elif t.state == tx.ZOMBIE:
        if t.zombie_out(): 
          del txs[key]
          yield t;
      elif t.timed_out():
        del txs[key]
    yield None

class Network(object):
  def __init__(self, db, addrs, me, master):
    self.master = master
    self.me = me
    self.db = db
    self.txs = {}
    self.getTxs = {}
    self.get = re.compile("GET (\[.*?\]) (\[.*?\])")
    self.put = re.compile("PUT (\[.*?\]) (\[.*?\]) (\[.*?\])")

    addrs.remove(me)
    self.addrs = addrs
    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.bind(me)
    self.next_zombie = check(self.txs)

  def __flood(self, orig, data):
    for a in filter(lambda x: x != orig, self.addrs):
      self.s.sendto(data, a)

  def make_ack(self, t, entry):
    return Packet(entry, self.master, t, self.me)

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
      if entry.key in self.putTxs:
        self.putTxs[(entry.key, entry.ts)].ack(entry)
    elif t == TYPE_GET:
      self.flood(self.make_ack(TYPE_GACK, db[entry.key]))
    elif t == TYPE_PUT:
      try:
        t = self.txs[(entry.key, entry.ts)]
        t.entry = entry
      except KeyError:
        t = Tx(self.db, entry)
        self.txs[(entry.key, entry.ts)] = t

      a = self.make_ack(TYPE_PACK, db[(entry.key, entry.ts)])
      t.ack(a.entry)
      if self.is_master:
        t.has_master = 1

      self.flood(a)
    elif t == TYPE_PACK:
      try:
        t = self.txs[(entry.key, entry.ts)]
      except KeyError:
        t = Tx(self.db, None)
        self.txs[(entry.key, entry.ts)] = t
      t.ack(entry)
      if m:
        t.has_master = 1

  def clientDispatch(self, data, addr):
    if data[0] == 'G':
      m = self.get.match(data)
      opaque = m.group(0)
      key = m.group(1)
      t = tx.GetTx(db, key, opaque, self.s, addr)
      self.getTxs[key] = t
    else:
      m = self.put.match(data)
      opaque = m.group(0)
      key = m.group(1)
      value = m.group(2)
      self.txs[key] = tx.PutTx(self.db, db.Entry(key, value, time.time()), opaque, self.s, addr)

  def poll(self):
    while True:
      zombie = next(self.next_zombie)
      if zombie is not None:
        self.rebroadcast(zombie)


      (data, addr) = self.s.recvfrom(10000)

      if data[0:3] == 'GET' or data[0:3] == 'PUT':
        self.clientDispatch(data, addr)
      else:
        pkt = pickle.loads(data)
        if self.has_seen(pkt): 
          continue

        self.see(pkt)
        self.dispatch(pkt.entry, pkt.type)
        self.__flood(addr, data)
