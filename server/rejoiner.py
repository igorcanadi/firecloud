

class Rejoiner(object):
  def __init__(self, network, db):
    self.network = network
    self.db = db

  def recv(self, pkt):
    def __():
      for ent in self.db.db.items():
        pkt = Packet(ent, None, TYPE_ACK, None)
        yield pkt
    for pkt in __():
      self.network.flood(pkt)

