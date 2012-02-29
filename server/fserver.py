import cPickle
import time
import random
import socket

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

class Pkt(object):
  def __init__(self, pkt, orig):
    self.orig = orig
    self.pkt = pickle.loads(pkt)
    self.id = pkt['id']

  # P put
  # A putack
  # G get
  # H getack
  def is_ack(self, pkt):
    t = self.pkt['t']
    return t == 'A' or t == 'H' or t == 'M' or t == 'N'

  def is_get(self, pkt):
    t = self.pkt['t']
    return t == 'G' or t == 'N'

  def is_master(pkt):
    return self.pkt['m']

  def make_ack(self, id):
    self.pkt['t'] = 'A' if pkt['t'] == 'P' else 'H'
    self.pkt['m'] = i_am_master()
    self.pkt['f'] = me()
    self.pkt['id'] = id 

  def make_orig(self):
    self.pkt['id'] = random.randint()
    self.id = self.pkt['id']

  def cooked():
    return pickle.dumps(self.pkt)
  
class Flooder(object):
  def __init__(self):
    self.tx = {}
    self.network = None
    self.msgs = set()
    self.acks = set()

  def recv(self, pkt):
    if pkt.is_ack():
      if pkt.id in self.acks:
        return
      else:
        self.dispatchAck(pkt)
        self.acks.add(id)
    else:
      if pkt.id in self.msgs:
        return
      else:
        self.dispatchMsg(pkt)
        self.msgs.add(id)

  def dispatchAck(self, pkt):
    if not pkt.is_get():
      try:
        self.tx[pkt.id].ack(pkt.is_master())
      except:
        t = Tx(None)
        t.ack(pkt)
        self.tx[pkt.id] = t;

    network.flood(pkt)

  def dispatchMsg(self, s, pkt):
    if pkt.is_get():
      network.floodAck(db.get(pkt))
    else:
      assert(pkt.id not in self.tx)

      self.tx[pkt.id] = Tx(pkt)

    network.flood(pkt)
    network.floodAck(pkt)

  def make_original(self, pkt):
    p = Pkt(pkt)
    p.make_orig()
    t = Tx(pkt)
    Tx.ack(pkt.is_master())

    self.tx[pkt.id] = t;
    network.flood(pkt)

class Datastore(object):
  def __init__(self):
    self.db = {}

  def val(self, key):
    return self.db[key]['val']

  def ts(self, key):
    return self.db[key]['ts']

  def get(self, d):
    key = d['key'];
    try:
      return {'s':'OK', 'val':val(key), 'ts':ts(key)};
    except KeyError:
      return {'s':'EM', 'val':'[]' 'ts':0}

  def put(self, d):
    key = d['key']
    try:
      r = {'s':'OK', 'val':val(key), 'ts':ts(key)}
    except KeyError:
      r = {'s':'OK', 'val':'[]', 'ts':0}
    
    if r['ts'] < d['ts']:
      self.db[key] = {'val':d['val'], 'ts':d['ts']}
    return r;


def Network(object):
  def __init__(self, addrs, me, master, flood):
    self.master = master
    self.me = me

    self.flood = flood
    flood.network = self

    addrs.remove(me)
    self.addrs = addrs
    self.s = socket.socket(AF_INET, socket.SOCK_DGRAM)
    self.s.bind(me)


  def flood(orig, pkt):
    c = pkt.cooked()
    for a in filter(lambda x: x != orig, self.addrs):
      self.s.sendto(c, a)

  def floodAck(pkt):
    ack = Pkt(pkt.pkt)
    ack.make_ack()
    c = ack.cooked()
    for a in self.addrs:
      self.s.sendto(pkt, a)

  def poll(self):
    while True:
      (data, addr) = self.s.recvfrom()
      pkt = Pkt(data)
      flood.recv(addr, pkt)

  def i_am_master(self):
    return self.master

def main():
  db = Datastore()
  flood = Flooder()
  n = Network(addrs, me, master, flood)

