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
    return t == 'A' or t == 'H'

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
  
