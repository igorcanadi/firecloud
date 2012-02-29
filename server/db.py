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

