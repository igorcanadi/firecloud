import time
from db import Entry

from logger import log, barf

UNCOMMITED = 0
COMMIT = 88
ZOMBIE = 1
DEAD = 3

FINISH = 78

normal = 1
master = 2

TIMEOUT = 2
ZOMBIE_TIMEOUT = 3


STATETBL = {
    0 : { master : (2, None),
          normal : (1, None) },
    1 : { master : (3, COMMIT),
          normal : (2, None) },
    2 : { master : (4, COMMIT),
          normal : (3, COMMIT) },
    3 : { master : (5, FINISH),
          normal : (4, None) },
    4 : { normal : (5, FINISH) },
    5 : { }
  }

def transition(state, arrow):
  try:
    return STATETBL[state][arrow]
  except KeyError:
    barf('INVALID State Transition: in state {0} with tranition of {1}'.format(state, arrow))
    raise Exception('Invalid State Transition -- see log.')
  return

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
    #if tx.entry is not None:
      # This is execute iff it is a PUT tx
    #  self.db.put(tx.entry)
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
    self.update = None
    self.start = time.time()
    self.net = net

  def timed_out(self, now):
    return now > self.start + TIMEOUT

  def revive(self, now):
    if now > self.start + ZOMBIE_TIMEOUT:
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
      self.state, action = transition(self.state, master)
    else:
      self.state, action = transition(self.state, normal)
    

    if action == COMMIT:
      self.commit()
    elif action == FINISH:
      self.finish()
