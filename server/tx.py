UNCOMMITED = 0
COMMITTED = 1
DEAD = 2

class Tx(object):
  def __init__(self, pkt):
    self.pkt = pkt;
    self.acks = 0
    self.state = UNCOMMITED
  def commit(self):
    if self.state != UNCOMMITED:
      return
    db.put(pkt);
  def ack(self, master):
    self.acks += 2 if master else 

    if self.acks >= 3:
      self.commit();
    if self.acks == 5:
      self.state = DEAD

class ClientTx(object):
  def __init__(self, client, pkt):
    Tx.__init__(pkt)
    self.client = client

  def commit(self):
    assert(self.pkt != None)
    res = db.put(pkt);
    self.client.send(res)

class Flooder(object):
  def __init__(self):
    self.tx = {}
    self.network = None
    self.msgs = set()
    self.acks = set()

