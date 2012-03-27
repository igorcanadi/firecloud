

"""
Does analysis across the outout 
"""

from cout import Get, Put, ClientTrace


class KVAnalysis(object):
  def __init__(self):
    self.kv = {}

  def __getitem__(self, name):
    if name not in self.kv:
      return '[]'
    return self.kv[name]

  def __setitem__(self, ke, name):
    if '[' not in name:
      name = '[' + name + ']'
    self.kv[ke] = name


def count_errors(ctrace):
  count = 0
  for tick, sec, evt, txt in ctrace:
    if txt is None:
      count += 1
  return count

def skip_errors(ctrace):
  for tick, sec, evt, txt in ctrace:
    if txt is None:
      continue
    yield (tick, sec, evt, txt)


def pretty_print(ctrace):
  for tick, sec, evt, txt in ctrace:
    print "%-4s  %d   %20s %20s" % (tick, sec, evt, txt)

def joint_print(*traces):
  joint = []
  for i, t in enumerate(traces):
    joint[0:0] = map( lambda x: (i, x), t )
  joint = sorted(joint, key=lambda x: x[1][1])

  for id, t in joint:
    l = [id] + list(t)
    print "%d %-4s  %d   %20s %20s" % tuple(l)

def stat_trace(ctrace):
  """ Returns a tuple of state for a trace
  (#reqs made, #errors, effective_time (secs), msec / req)
  """
  return ctrace.reqcount, count_errors(ctrace), ctrace.slack, ctrace.slack * 1000.0 / ctrace.reqcount

def ticks_in_order(ctrace):
  """ Determines if all ticks came back in order
  """
  last_tick = -1
  for tick, sec, evt, txt in ctrace:
    if tick < last_tick:
      return False
  return True


def merge_traces(t0, t1):
  joint = t0.trace[:]
  joint[0:0] = t1.trace[:]
  joint = sorted(joint, key=lambda x: x[1])
  return ClientTrace(joint, t0.slack + t1.slack,
                     t0.reqcount+t1.reqcount,
                     0)
  

def eval_strict_ordering(ctrace, verbose=True):
  """ Returns true if everything was ordered exactly
  as it was scheduled, otherwise false
  @return: a count of how many ops had unexpected results
  """
  kv = KVAnalysis()
  errors = 0
  for tick, ti, evt, resl in skip_errors(ctrace):
    if isinstance(evt, Put):
      oldv = kv[evt.ke]
      if oldv != resl:
        if verbose:
          print tick, 'Expected', oldv, resl
        errors += 1
      kv[evt.ke] = evt.val
    elif isinstance(evt, Get):
      oldv = kv[evt.ke]
      if oldv != resl:
        if verbose:
          print tick, 'Expected', oldv, resl
        errors += 1
        # correct for the error
        kv[evt.ke] = resl
  return errors


def split_puts_by_key(trace):
  kes = {}
  for tick, ti, evt, resl in skip_errors(trace):
    if isinstance(evt, Put):
      if evt.ke not in kes:
        kes[evt.ke] = []
      kes[evt.ke].append((tick, ti, evt, resl))
  return kes


def eval_fuzzy_order_by_key(trace):
  kes = split_puts_by_key(trace)
  for ke in kes:
    kes[ke] = eval_fuzzy_order(kes[ke])
  return kes


def eval_fuzzy_order(trace):
  """ Assumes only 1 key was used. 
  Assuems values are 'client_id unique-increasing-value'
  """
  g = {}
  start = []
  for tick, ti, evt, resl in skip_errors(trace):
    resl = resl.lstrip('[').rstrip(']')
    if isinstance(evt, Put):
      cl0, v0 = evt.val.split(' ')
      if resl == '':
        start.append((cl0, v0))
        continue
      cl1, v1 = resl.split(' ')

      if (cl1, v1) in g:
        print '** No ordering -- repeated get (revisting: {0} from {1}).'.format((cl1, v1), (cl0, v0))
        return False

      g[(cl1,  v1)] = (cl0, v0)

  # graph built

  # find a starting point, a node with no enterance
  pos = start

  if len(pos) != 1:
    print '** No (single) starting point.'
    return False

  cur = pos[0]

  last_used = {}

  visited = 0
  while True:
    visited += 1
    c, v = cur
    if c in last_used:
      if int(v) <= int(last_used[c]):
        print '**Back Tracking'
        return False
    last_used[c] = v

    if cur not in g:
      break;

    cur = g[cur]

  if visited != len(g) + 1:
    print '**Visited: {0} out of {1}'.format(visited, len(g) + 1)
    return False
  #print 'walk is good!'
  return True


def eval_put_ordering(ctrace):
  """ Determines if there some ordering for the puts,
  even if it isn't the ordering we thought we would get
  @return: a count of how many ops had unexpected results
  """
  # FIXME, this is just copied
  # TODO do this correctly
  for tick, ti, evt, resl in ctrace:
    if isinstance(evt, Put):
      oldv = kv[evt.ke]
      if oldv != resl:
        errors += 1
      kv[evt.ke] = evt.val


def replay_gets_into_dict(ctrace):
  """ Builds a dict from the result of get ops, ignores put ops
  @rtype: dict
  @return: a dict based on gets
  """
  d = {}
  for tick, ti, evt, resl in ctrace:
    if isinstance(evt, Get):
      d[evt.ke] = resl
  return d

def check_traces_ordering(traces):
  graph = {}
  for tick, ti, evt, resl in ctrace:
    graph[resl] = evt.val

