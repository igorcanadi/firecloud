UNCOMMITED = 0
ZOMBIE = 1
DEAD = 3

TIMEOUT = 2
ZOMBIE_TIMEOUT = 3

class Tx(object):
  def __init__(self, db, entry):
    self.entry = entry
    self.acks = set()
    self.state = UNCOMMITED
    self.start = time.time()
    self.has_master = 0

  def timed_out(self):
    return time.time() > self.start + TIMEOUT

  def zombie_out(self):
    return time.time() > self.start + ZOMBIE_TIMEOUT

  def commit(self):
    if self.state != UNCOMMITED:
      return
    db.put(pkt);

  def ack(self, ack):
    self.acks.add(ack)

    if len(self.acks) + self.has_master >= 3 and self.state == UNCOMMITED:
      self.state = ZOMBIE
      self.commit()

    if len(self.acks) + self.has_master == 5:
      self.state = DEAD

  def send_res(self, val):
    self.sock.sendto("OK [%s] [%s]" % (self.opaque, val), self.addr)

class PutTx(Tx):
  def __init__(self, key, opaque, value, sock, addr):
    Tx.__init__(pkt)
    self.addr = addr
    self.sock = sock
    self.opaque = opaque
    self.kv = (key, value)

  def commit(self):
    db.put(self.kv);
    ack = reduce(lambda x,y: x if x.ts > y.ts else y, self.acks)
    self.send_res(ack.val)
    
class GetTx(Tx):
  def __init__(self, key, opaque, sock, addr):
    Tx.__init__(pkt)
    self.addr = addr
    self.sock = sock
    self.opaque = opaque
    self.k = key

  def commit(self):
    ack = reduce(lambda x,y: x if x.ts > y.ts else y, self.acks)
    self.send_res(ack.val)
