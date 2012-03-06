from collections import namedtuple

Entry = namedtuple('Entry', ['key', 'ts', 'val'])

class Datastore(object):
  def __init__(self):
    self.db = {}

  def val(self, key):
    #return self.db[key]['val']
    return self.db[key].val

  def ts(self, key):
    return self.db[key].ts
    #return self.db[key]['ts']

  def get(self, d):
    key = d['key'];
    try:
      return {'val':val(key), 'ts':ts(key)};
    except KeyError:
      return {'val':'[]', 'ts':0}

  def put(self, d):
    key = d['key']
    try:
      r = {'val':val(key), 'ts':ts(key)}
    except KeyError:
      r = {'val':'[]', 'ts':0}
    
    if r['ts'] < d['ts']:
      self[key] = Entry(d['val'], d['ts'])
    return r;

  def __getitem__(self, ke):
    if ke not in self.db:
      return None
    return self.db[ke]

  def __setitem__(self, ke, val):
    if (ke not in self.db) or (self.db[ke].ts < val.ts):
      self.db[ke] = val
