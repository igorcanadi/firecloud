import cPickle as pickle
import socket
from collections import namedtuple
import tx
import re
import db
import time
import random

from logger import log, barf

Packet = namedtuple('Packet', ['entry', 'is_master', 'type', 'orig', 'seq', 'clock'])

TYPE_PUT = 'P'
TYPE_PACK = 'A'
TYPE_GET = 'G'
TYPE_GACK = 'H'

server_pkts_sent  = 0
server_pkts_recved = 0

client_pkts_sent = 0
client_pkts_recved = 0

clock = 0

def inc_clock():
  global clock
  clock += 3

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
    self.rebroadcasts = []
    self.get = re.compile("GET (\[.*?\]) (\[.*?\])")
    self.put = re.compile("PUT (\[.*?\]) (\[.*?\]) (\[.*?\])")
    self.last_zombie = time.time()

    self.seen1 = set()
    self.seen2 = set()

    addrs.remove(me)
    self.addrs = addrs
    self.r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    ###print 'I AM:', me
    self.r.bind(me)

    self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

  def __flood(self, orig, data):
    global server_pkts_sent
    for a in filter(lambda x: x != orig, self.addrs):
      server_pkts_sent += 1
      self.s.sendto(data, a)

  def flood_ack(self, t, entry, seq):
    assert type(entry.key) is str
    inc_clock()
    self.__flood(None, pickle.dumps((tuple(entry), self.master, t, self.me, seq, clock), 2))

  def has_seen(self, pkt):
    return (pkt.clock, pkt.orig) in self.seen1 or (pkt.clock, pkt.orig) in self.seen2

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
    self.seen1.add((pkt.clock, pkt.orig))

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

    global server_pkts_sent
    server_pkts_sent += 1
    self.s.sendto(pkt, self.me)

  def rebroadcast(self, tx):
    self.rebroadcasts.append(tx.entry)

  def check(self, now):
    znum = 0
    tonum = 0
    for key in self.txs.keys():
      t = self.txs[key]
      if t.state == tx.ZOMBIE:
        znum += t.revive(now)
        continue
      if t.timed_out(now):
        tonum += 1
        del self.txs[key]
    return (znum, tonum)


  def bookkeep(self, now):
    len1 = len(self.seen1)
    len2 = len(self.seen2)
    self.seen2 = self.seen1
    self.seen1 = set()
    
    barf("over a %s sec period" % (str(now - self.last_zombie)))
    self.last_zombie = now
    (z,t) = self.check(now)
    barf("zombie %d timeout %d" % (z,t))
    barf("%s srv out %d : srv in %d ;; cl out %d : cl in %d" % (str(self.me), server_pkts_sent, server_pkts_recved, client_pkts_sent, client_pkts_recved))
    barf("txs %d : rebroadcast queue %d : listeners %d" % (len(self.txs), len(self.rebroadcasts), len(self.listeners)))
    barf("ack seen1 %d : ack seen2 %d" % (len1, len2))

  def poll(self):
    global client_pkts_recved
    global server_pkts_recved
    while True:
      now = time.time()
      if now > (self.last_zombie + random.uniform(.8, 2)): 
        self.bookkeep(now)
        
      try:
        entry = self.rebroadcasts.pop()
        self.flood_ack(TYPE_PACK, entry, random.random())
      except IndexError:
        pass

      (data, addr) = self.r.recvfrom(4096)

      if data[0:4] == 'ping':
        self.r.sendto('pong', addr)
        continue


      if data[0:3] == 'GET' or data[0:3] == 'PUT':
        client_pkts_recved += 1
        log('NET :: ' + data)
        self.clientDispatch(data, addr)
      else:
        server_pkts_recved += 1
        try:
          t = pickle.loads(data)
        except:
          log('Got bad packet: ' + str(data))
          continue


        global clock
        clock = max(t[5], clock) + 1

        pkt = Packet._make((db.Entry._make(t[0]), t[1], t[2], t[3], t[4], t[5]))
        if self.has_seen(pkt): 
          continue

        ##print pkt
        self.see(pkt)
        assert type(pkt.entry.key) is str
        self.__flood(addr, data)
        yield pkt
