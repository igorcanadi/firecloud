from collections import namedtuple
from logger import log



Entry = namedtuple('Entry', ['key', 'ts', 'val'])

class Datastore(object):
  def __init__(self):
    self.db = {}

  def make_empty_entry(self, key):
    assert type(key) is str
    return Entry(key, 0, '[]')

  def put(self, ent):
    assert type(ent) is Entry
    self[ent.key] = ent

  def __getitem__(self, ke):
    assert type(ke) is str
    if ke not in self.db:
      return self.make_empty_entry(ke)
    log('DB :: GET {0} = {1}'.format(ke, self.db[ke]))
    return self.db[ke]

  def __setitem__(self, ke, val):
    #print val
    assert type(ke) is str
    assert type(val) == Entry
    if (ke not in self.db) or (self.db[ke].ts < val.ts):
      log('DB :: PUT {0} = {1}'.format(ke, val))
      self.db[ke] = val

