


def simplest_test(sys):
  """ Store a single key and check it's value
  """
  kv = sys.store

  kv['key'] = 'value'
  kv['key']


def simple_single_key(sys):
  kv = sys.store

  # check to make sure the key has no value
  kv['capel']

  # give it a value
  kv['capel'] = 'watch out'

  # check it's value
  kv['capel']

  # change its value
  kv['capel'] = 'its a trap'

  # check it got the right second value
  kv['capel']

  # check it again, just in case
  kv['capel']

  # maybe they didn't see the 3rd time coming....
  kv['capel']

  # check that we can count with it
  for i in xrange(10):
    kv['capel'] = i
    kv['capel']

def simple_2key(sys):
  kv = sys.store
  
  # check initial states
  kv['i love'] 
  kv['i hate']

  kv['i hate'] = 'monkies'
  kv['i love'] = 'distributed systems'

  # check expected values
  kv['i love'] 
  kv['i hate']

  kv['i hate'] = 'nothing'
  kv['i love'] 
  kv['i hate']
  kv['i love'] = 'everything'
  kv['i love'] 
  kv['i hate']

  vals = zip(range(100, 110), range(200, 210))
  for x, y in vals:
    kv['i love'] = x
    kv['i love'] 
    kv['i hate']
    kv['i hate'] = y
    kv['i love'] 
    kv['i hate']


def simple_many_keys(sys):
  kv = sys.store
  kes = range(50)
  values = range(50, 100)

  for k, v in zip(kes, values):
    kv[k] = v


def many_vals_many_keys(sys):
  kv = sys.store
  kes = range(50)

  for r in xrange(5):
    for k in kes:
      kv[k]
      kv[k] = r + k
      kv[k]
    
  for k in kes:
    kv[k]
