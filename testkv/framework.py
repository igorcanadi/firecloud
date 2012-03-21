from collections import namedtuple
from cout import Init
from transcribe import PutEvent, GetEvent, NetKillEvent, NetUpEvent, \
                       HostKill, HostUp, FailEvent, RecoverEvent
from conf import CLOCK_RATE, PRE_NETWORK_WINDOW, POST_NETWORK_WINDOW


class Server(object):
  def __init__(self, xcript, host, port):
    self.host = host
    self.port = port
    self.xcript = xcript

  def fail(self):
    self.xcript.record(HostKill(self.host, self.port))

  def recover(self):
    self.xcript.record(HostUp(self.host, self.port))
  
  def __str__(self):
    return '{0.host}:{0.port}'.format(self)


class Client(object):
  def __init__(self, clock, nodes):
    self.clock = clock
    self.xcript = Transcript(clock)
    self.nodes = nodes
    self.store = KVStore(self.xcript)
    self.xcript.record(Init(map(str, nodes)))

  def fail(self, node):
    self.xcript.record(FailEvent(node.host, node.port))

  def recover(self, node):
    self.xcript.record(RecoverEvent(node.host, node.port))


class Clock(object):
  def __init__(self):
    self.time = 0

  def tick(self, ticks=1):
    self.time += ticks
    return self.time


class Transcript(object):
  def __init__(self, clock):
    self.clock = clock
    self.log = []

  def record(self, event):
    self.log.append((self.clock.tick(), event))


class Network(object):
  def __init__(self, nodes, xcript):
    self.xcript = xcript
    self.nodes = nodes
    self.edges = {}
    for a in nodes:
      for b in nodes:
        if a == b:
          continue

  def __setitem__(self, (a, b), val):
    if b < a:
      t = a
      a = b
      b = a
    if val:
      self.xcript.record(NetUpEvent(a, b))
    else:
      self.xcript.record(NetKillEvent(a, b))
    self.edges[(a, b)] = False

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
      self.xcript.record(PutEvent(name, val))
    else:
      self.xcript.record(PutEvent(name, val))
    self.store[name] = val

  def __getitem__(self, name):
    if name in self.store:  
      self.xcript.record(GetEvent(name))
    else:
      self.xcript.record(GetEvent(name))
      return None
    return self.store[name]

  def keys(self):
    return self.store.keys()

  def __iter__(self):
    return self.store.__iter__()


