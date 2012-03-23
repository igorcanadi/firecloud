import time
from db import Entry
import net

from logger import log, barf

UNCOMMITED = 0
COMMIT = 88
ZOMBIE = 1
DEAD = 3

FINISH = 78

normal = 'A'
master = 'M'

TIMEOUT = 1
ZOMBIE_TIMEOUT = 1

def tm(m, n, mact = None, nact = None):
  return { master: (m, mact), normal: (n, nact) }

STATETBL = {
    'init' : tm('M', 'A'),
    'A' : tm('MA', 'AA', mact=COMMIT),
    'AA' : tm('MAA', 'AAA', mact=COMMIT, nact=COMMIT),
    'AAA' : tm('MAAA', 'D', mact=FINISH),
    'M' : tm('D', 'MA', nact=COMMIT),
    'MA' : tm('D', 'MAA'),
    'MAA' : tm('D', 'MAAA', nact=FINISH),
    'MAAA' : tm('D', 'D'),
  }

def transition(state, arrow):
  (new_state, action) = STATETBL[state][arrow]
  if new_state == 'D':
    barf('INVALID State Transition: {0} - {1} -> {2}'.format(state, arrow, new_state))
    raise Exception('Invalid State Transition -- see log.')

  return (new_state, action)

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
    self.state = 'init'
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
      return 1
    return 0

  def finish(self):
    self.net.finish(self)

  def commit(self):
    self.net.commit(self)

  def ack(self, entry, is_master):
    assert type(entry.key) is str
    if self.entry is None or entry.ts > self.entry.ts:
      self.entry = entry

    try:
    if int(is_master) != 0:
        self.state, action = transition(self.state, master)
      else:
        self.state, action = transition(self.state, normal)
    except TypeError:
      return
    

    if action == COMMIT:
      self.commit()
    elif action == FINISH:
      self.finish()
