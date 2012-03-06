def Dispatch(object):
  def __init__(self, log, rejoiner):
    self.log = log
    self.rejoiner = rejoiner

  def dispatch(self):
    p = Pkt(pkt)
    t = p.type
    if t == 'A':
      log.recvAck(p)
    elif t == 'P':
      log.recvPut(p)
    elif t == 'G':
      log.recvGet(p)
    elif t == 'R':
      log.recv(p)
