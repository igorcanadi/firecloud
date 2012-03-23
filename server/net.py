import cPickle as pickle
import socket
from collections import namedtuple
import tx
import re
import db
import time
import random


from logger import log, barf


TYPE_PUT = 'P'
TYPE_PACK = 'A'
TYPE_GET = 'G'
TYPE_GACK = 'H'


import flooder

class Dispatcher(object):
  def __init__(self):
    pass

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
    print typ
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
    self.db = db
    self.txs = {}
    self.listeners = {}
    self.me = me

    self.get = re.compile("GET (\[.*?\]) (\[.*?\])")
    self.put = re.compile("PUT (\[.*?\]) (\[.*?\]) (\[.*?\])")

    self.dispatcher = Dispatcher()
    self.flooder = flooder.Flooder(addrs, me, int(master))

    self.clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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
    self.flooder.send(self.db[key], TYPE_GACK, seq)

  def flood_pack_for_key(self, key, seq):
    self.flooder.send(self.db[key], TYPE_PACK, seq)

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
    flooder.clock.inc()
    seq = random.random()
    e = db.Entry(key, (flooder.clock, self.me), self.db[key].val)

    self.listeners[seq] = tx.Listener(self.db, opaque, self.clientSock, addr)

    t = tx.Tx(self, seq)
    self.txs[seq] = t

    self.flooder.send(e, TYPE_GET, seq)
    self.flood_gack_for_key(key, seq)

  def clientPut(self, key, value, opaque, addr):
    flooder.clock.inc()
    seq = random.random()
    e = db.Entry(key, (flooder.clock, self.me), value)

    self.listeners[seq] = tx.Listener(self.db, opaque, self.clientSock, addr)

    t = tx.Tx(self, seq)
    self.txs[seq] = t

    self.flooder.send(e, TYPE_PUT, seq)
    self.flood_pack_for_key(key, seq)

  def loop(self):
    for (variety, req) in self.flooder:
      if variety == flooder.SERVER:
        entry, typ, seq, m = req
        self.dispatcher.dispatch(entry, seq, typ, m)
      else:
        data, addr = req
        self.clientDispatch(data, addr)
