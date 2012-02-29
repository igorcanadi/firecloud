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
