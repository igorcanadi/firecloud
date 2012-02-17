from collections import namedtuple


PutEvent = namedtuple('Put', ['k', 'v', 'oldv'])
GetEvent = namedtuple('Get', ['k', 'v'])
NetKillEvent = namedtuple('NetKill', ['host0', 'host1'])
NetUpEvent = namedtuple('NetUp', ['host0', 'host1'])


class Server(object):
  def __init__(self, host, port):
    self.host = host
    self.port = port


class System(object):
  def __init__(self, clock, nodes):
    self.nodes = nodes
    self.clock = clock
    self.xcript = Transcript(clock)
    self.network = Network(nodes, self.xcript)
    self.store = KVStore(self.xscript)
    self.status = Fasle


class Clock(object):
  def __init__(self):
    self.time = 0

  def tick(self):
    self.time += 1
    return self.time


class Transcript(object):
  def __init__(self, clock):
    self.clock = clock
    self.log = []

  def record(event):
    self.log.append((clock.tick(), event))


class Network(object):
  def __init__(self, nodes, xcript):
    self.xcript = xcript
    self.nodes = nodes
    self.edges = {}
    for a in nodes:
      for b in nodes:
        if a == b:
          continue

  def __setitem__(self, (a, b), val)
    if b < a:
      t = a
      a = b
      b = a
    if val:
      self.xcript.record(NetUpEvent(a, b))
    else:
      self.xcript.record(NetKillEvent(a, b))
    edges[(a, b)] = False

  def __getitem__(self, (a, b)):
    if b < a:
      t = a
      a = b
      b = a
    return edges[(a, b)] 


class KVStore(object):
  def __init__(self, xcript):
    self.xcript = xcript
    self.store = {}

  def __setitem__(self, name, val):
    val = str(val)
    assert '[' not in val
    assert ']' not in val
    name = str(name)
    assert '[' not in name
    assert ']' not in name
    if name in self.store:  
      self.xcript.record(PutEvent(name, val, self.store[name]))
    else:
      self.xcript.record(PutEvent(name, val, None))
    self.store[name] = val

  def __getitem__(self, name):
    if name in self.store:  
      self.xcript.record(GetEvent(name, self.store[name]))
    else:
      self.xcript.record(GetEvent(name, None))
    return self.store[name]

  def keys(self):
    return self.store.keys()

  def __iter__(self):
    return self.store.__iter__()


