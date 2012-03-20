import time
from db import Entry

from logger import log

UNCOMMITED = 0
ZOMBIE = 1
DEAD = 3

TIMEOUT = 2
ZOMBIE_TIMEOUT = 3



def transition(state, arrow):
  if state == 0:
    if arrow == master:
      return (2, None);
    elif arrow == normal:
      return (1, None);
    else:
      assert(0)

  if state == 1:
    if arrow == master:
      return (3, COMMIT);
    elif arrow == normal:
      return (2, None);
    else:
      assert(0)

  if state == 2:
    if arrow == master:
      return (4, COMMIT);
    elif arrow == normal:
      return (3, COMMIT);
    else:
      assert(0)

  if state == 3:
    if arrow == master:
      return (5, FINISH);
    elif arrow == normal:
      return (4, None);
    else:
      assert(0)

  if state == 4:
    if arrow == master:
      assert(0)
    elif arrow == normal:
      return (5, FINISH);
    else:
      assert(0)

  if state == 5:
    assert(0)



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
    self.state = 0
    self.seq = seq
    self.start = time.time()
    self.update = None
    self.net = net

  def timed_out(self):
    return time.time() > self.start + TIMEOUT

  def zombie(self):
    if time.time() > self.start + ZOMBIE_TIMEOUT:
      self.net.rebroadcast(self)
      self.net.finish(self)

  def finish(self):
    self.net.finish(self)

  def commit(self):
    self.net.commit(self)

  def ack(self, entry, is_master):
    assert type(entry.key) is str
    if self.entry is None or entry.ts > self.entry.ts:
      self.entry = entry

    if is_master:
      self.state, action = transition(self.state, MASTER)
    else:
      self.state, action = transition(self.state, NORMAL)

    if action == COMMIT:
      self.commit()
    elif action == FINISH:
      self.finish()
