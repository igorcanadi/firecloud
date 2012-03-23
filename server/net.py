import cPickle as pickle
import socket
from collections import namedtuple
import tx
import re
import db
import time

from netlayer import BufSocket

from logger import log, barf

Packet = namedtuple('Packet', ['entry', 'is_master', 'type', 'orig', 'seq', 'clock'])

TYPE_PUT = 'P'
TYPE_PACK = 'A'
TYPE_GET = 'G'
TYPE_GACK = 'H'

clock = 0

def inc_clock():
  global clock
  clock += 3

class EventLoop(object):
  def __init__(self, network):
    self.network = network

  def poll(self):
    while True:
      self.network.drain(self)

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

class Flooder(object):
  def __init__(self, addrs, me, master, net):
    self.addrs = addrs
    self.r = BufSocket(me, net)
    self.me = me
    self.master = master

  def flood(self, orig, data):
    for a in filter(lambda x: x != orig, self.addrs):
      self.r.sendto(data, a)

  def flood_ack(self, t, entry, seq):
    assert type(entry.key) is str
    inc_clock()
    self.flood(None, (tuple(entry), self.master, t, self.me, seq, clock))

class Network(object):
  def __init__(self, db, addrs, me, master):
    self.master = int(master)
    self.me = me
    self.db = db
    self.txs = {}
    self.listeners = {}
    self.get = re.compile("GET (\[.*?\]) (\[.*?\])")
    self.put = re.compile("PUT (\[.*?\]) (\[.*?\]) (\[.*?\])")
    self.next_zombie = time.time() + 1

    self.flooder = Flooder(addrs, me, self.master, self)

    self.seen1 = set()
    self.seen2 = set()

    addrs.remove(me)
    #self.r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ###print 'I AM:', me
    #self.r.bind(me)

    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def has_seen(self, clock, origin):
    return (clock, origin) in self.seen1 or (clock, origin) in self.seen2

  def see(self, clock, origin):
    self.seen1.add((clock, origin))

  def commit(self, tx):
    try:
      self.listeners[tx.seq].commit(tx) 
      del self.listeners[tx.seq]
    except KeyError:
      pass
    if tx.update is not None:
      self.db.put(tx.update)

  def finish(self, tx):
    del self.txs[tx.seq]

  def flood_gack_for_key(self, key, seq):
    self.flooder.flood_ack(TYPE_GACK, self.db[key], seq)

  def flood_pack_for_key(self, key, seq):
    self.flooder.flood_ack(TYPE_PACK, self.db[key], seq)

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
      opaque = m.group(2)
      self.clientGet(key, opaque, addr)
    else:
      m = self.put.match(data)
      key = m.group(1)
      value = m.group(2)
      opaque = m.group(3)
      self.clientPut(key, value, opaque, addr)

  def clientGet(self, key, opaque, addr):
    inc_clock()
    e = db.Entry(key, (clock, self.me), self.db[key].val)

    self.listeners[opaque] = tx.Listener(self.db, opaque, self.s, addr)

    t = tx.Tx(self, opaque)
    self.txs[opaque] = t

    pkt = (tuple(e), self.master, TYPE_GET, self.me, opaque, clock)
    self.flooder.flood(self.me, pkt)
    self.flood_gack_for_key(key, opaque)

  def clientPut(self, key, value, opaque, addr):
    inc_clock()
    e = db.Entry(key, (clock, self.me), value)

    self.listeners[opaque] = tx.Listener(self.db, opaque, self.s, addr)

    t = tx.Tx(self, opaque)
    self.txs[opaque] = t

    pkt = (tuple(e), self.master, TYPE_PUT, self.me, opaque, clock)
    self.flooder.flood(self.me, pkt)
    self.flood_pack_for_key(key, opaque)

  def process(self, loop, req, addr):
    if type(req) is str:
      self.clientDispatch(req, addr)
    else:
      barf("type " + str(type(req)) + " len " + str(len(req)))
      assert type(req) is tuple and len(req) == 6
      (entry, m, typ, origin, seq, other_clock) = req
      entry = db.Entry._make(entry)

      global clock
      clock = max(other_clock, clock) + 1

      if not self.has_seen(other_clock, origin): 
        self.see(other_clock, origin)
        self.flooder.flood(addr, req)
        loop.dispatch(entry, seq, typ, m)

  def drain(self, loop):
    for (req, addr) in self.flooder.r:
      self.process(loop, req, addr)

    self.flooder.r.batch_send()
    self.flooder.r.batch_recv()
