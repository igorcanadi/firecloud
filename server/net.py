import cPickle as pickle
import socket
from collections import namedtuple
import tx
import re
import db
import time
import random

from logger import log

Packet = namedtuple('Packet', ['entry', 'is_master', 'type', 'orig', 'seq', 'clock'])

TYPE_PUT = 'P'
TYPE_PACK = 'A'
TYPE_GET = 'G'
TYPE_GACK = 'H'

clock = 0

def inc_clock():
  global clock
  clock += 3

def check(t, net, now):
  for key in net.txs.keys():
    t = net.txs[key]
    if t.state == tx.ZOMBIE:
      t.revive(now)
      return
    if t.timed_out(now):
      del txs[key]

class EventLoop(object):
  def __init__(self, network):
    self.network = network

  def poll(self):
    """ Infinitely handle packets as they arrive """
    for pkt in self.network.poll():
      self.dispatch(pkt.entry, pkt.seq, pkt.type, pkt.is_master)

  def dispatch(self, entry, seq, typ, m):
    """ Recieves a packet contents form lower level network layer
    and dispatches it to the correct higher level handlers.
    """
    assert type(entry.key) is str
    handlers = {
        TYPE_GACK : self._handle_get_ack,
        TYPE_GET : self._handle_get,
        TYPE_PUT : self._handle_put,
        TYPE_PACK : self._handle_put_ack
      }
    assert typ in handlers
    handlers[typ](entry, seq, typ, m)

  def _handle_get_ack(self, entry, seq, typ, mast):
    """ Snoop and add it to our DB,
    count the ACK only if we have an open transaction for it
    """
    self.network.db.put(entry)
    self.network.ack_get_xact(entry, seq, mast)

  def _handle_get(self, entry, seq, typ, mast):
    """ Flood our current value for that key
    """
    self.network.flood_gack_for_key(entry.key, seq)

  def _handle_put(self, entry, seq, typ, mast):
    """ Open the transaction and flood our ACK of it 
    """
    myentry = self.network.db[entry.key]
    # XXX wtf is update?
    # XXX FIXME This is really baaaad
    self.network.set_put_xact_value(entry, seq)
    self.network.flood_pack_for_key(entry.key, seq)
  
  def _handle_put_ack(self, entry, seq, typ, mast):
    """ Record the ACK for the associated transaction
    """
    log('PACK for ' + str(entry) + str(mast))
    self.network.ack_put_xact(entry, seq, mast)


class Network(object):
  def __init__(self, db, addrs, me, master):
    self.master = int(master)
    self.me = me
    self.db = db
    self.txs = {}
    self.listeners = {}
    self.seen = set()
    self.get = re.compile("GET (\[.*?\]) (\[.*?\])")
    self.put = re.compile("PUT (\[.*?\]) (\[.*?\]) (\[.*?\])")
    self.last_zombie = time.time()

    addrs.remove(me)
    self.addrs = addrs
    self.r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ###print 'I AM:', me
    self.r.bind(me)

    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.s.setsockopt(socket.SO_BROADCAST)

  def __flood(self, orig, data):
    self.s.sendto(data, ("192.168.56.255", 8808))
    #for a in filter(lambda x: x != orig, self.addrs):
    #  self.s.sendto(data, a)

  def flood_ack(self, t, entry, seq):
    assert type(entry.key) is str
    inc_clock()
    self.__flood(None, pickle.dumps((tuple(entry), self.master, t, self.me, seq, clock), 2))

  def has_seen(self, pkt):
    return (pkt.clock, pkt.orig) in self.seen

  def commit(self, tx):
    ##print 'Commit: ', tx.entry
    log('COMMIT: %s' % str(tx.update))
    try:
      ##print self.listeners
      self.listeners[tx.seq].commit(tx) 
      del self.listeners[tx.seq]
    except KeyError:
      pass
      ##print 'Didnt find: ', (tx.seq)
    if tx.update is not None:
      self.db.put(tx.update)

  def finish(self, tx):
    del self.txs[tx.seq]

  def see(self, pkt):
    self.seen.add((pkt.clock, pkt.orig))

  def flood_gack_for_key(self, key, seq):
    self.flood_ack(TYPE_GACK, self.db[key], seq)

  def flood_pack_for_key(self, key, seq):
    self.flood_ack(TYPE_PACK, self.db[key], seq)

  def ack_get_xact(self, entry, seq, mast):
    try:
      self.txs[seq].ack(entry, mast)
    except KeyError:
      pass

  def set_put_xact_value(self, entry, seq):
    try:
      t = self.txs[seq]
    except KeyError:
      t = tx.Tx(self, seq)
      self.txs[seq] = t
    log(':: Set Xact Update to ' + str(entry))
    t.update = entry

  def ack_put_xact(self, entry, seq, mast, update=False):
    try:
      t = self.txs[seq]
    except KeyError:
      t = tx.Tx(self, seq)
      self.txs[seq] = t

    t.ack(entry, mast)
  
  def clientDispatch(self, data, addr):
    ##print data
    if data[0] == 'G':
      m = self.get.match(data)
      key = m.group(1)
      ##print 'Matched to: key: ', key
      opaque = m.group(2)
      value = None
      type_ = TYPE_GET
    else:
      m = self.put.match(data)
      key = m.group(1)
      value = m.group(2)
      ##print 'Matched to: value: ', value
      opaque = m.group(3)
      type_ = TYPE_PUT

    inc_clock()
    r = random.random()
    ##print key
    assert type(key) is str
    e = db.Entry(key, (clock, self.me), value if type_ == TYPE_PUT else self.db[key].val)
    self.listeners[r] = tx.Listener(self.db, opaque, self.s, addr)
    if type_ == TYPE_GET:
      t = tx.Tx(self, r)
      self.txs[r] = t

    ##print self.db[key]
    assert type(e.key) is str
    inc_clock()
    pkt = pickle.dumps((tuple(e), self.master, type_, self.me, r, clock), 2)
    self.s.sendto(pkt, self.me)

  def rebroadcast(self, tx):
    self.flood_ack(TYPE_PACK, tx.entry, tx.seq)


  def poll(self):
    while True:
      now = time.time()
      if now > self.last_zombie + random.uniform(.5, 2): 
        self.last_zombie = now
        #check(net, self.txs, now)

      (data, addr) = self.r.recvfrom(10000)

      if data[0:3] == 'GET' or data[0:3] == 'PUT':
        log('NET :: ' + data)
        self.clientDispatch(data, addr)
      else:
        t = pickle.loads(data)

        global clock
        clock = max(t[5], clock) + 1

        pkt = Packet._make((db.Entry._make(t[0]), t[1], t[2], t[3], t[4], t[5]))
        if self.has_seen(pkt): 
          continue

        ##print pkt
        self.see(pkt)
        yield pkt
        assert type(pkt.entry.key) is str
        self.__flood(addr, data)
