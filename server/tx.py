import time
from db import Entry

from logger import log

UNCOMMITED = 0
ZOMBIE = 1
DEAD = 3

TIMEOUT = 2
ZOMBIE_TIMEOUT = 3

class Listener(object):
  def __init__(self, db, opaque, sock, addr):
    self.opaque = opaque
    self.db = db
    self.sock = sock
    self.addr = addr

  def commit(self, tx):
    #print 'Operating on', tx
    #print "::: COMMITTTT'N  UPDATE:", tx.update 
    if tx.update is not None:
      self.db.put(tx.update)
    #print tx.entry
    # send old (or current) value
    #print "sending to client:"
    log('TX to Client :: OK %s %s' % (self.opaque, tx.entry.val))
    self.sock.sendto("OK %s %s" % (self.opaque, tx.entry.val), self.addr)

class Tx(object):
  def __init__(self, net, seq):
    self.entry = None
    self.acks = 0
    self.seq = seq
    self.state = UNCOMMITED
    self.start = time.time()
    self.update = None
    self.net = net

  def timed_out(self):
    return time.time() > self.start + TIMEOUT

  def zombie_out(self):
    return time.time() > self.start + ZOMBIE_TIMEOUT

  def commit(self):
    self.net.commit(self)

  def ack(self, entry, is_master):
    assert type(entry.key) is str
    if self.entry is None or entry.ts > self.entry.ts:
      self.entry = entry

    self.acks += 2 if is_master else 1

    log('   @ ' + str(self.acks) + ' acks; added ' + ('2' if is_master else '1'))

    if self.acks >= 3 and self.state == UNCOMMITED:
      self.state = ZOMBIE
      self.commit()

    if self.acks == 5:
      self.state = DEAD
