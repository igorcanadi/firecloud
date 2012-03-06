import cPickle
import time
import random
import socket

import db

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



def main():
  db = db.Datastore()
  flood = Flooder()
  n = Network(addrs, me, master, flood)

