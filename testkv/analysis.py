

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
  

def eval_strict_ordering(ctrace):
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
        print tick, 'Expected', oldv, resl
        errors += 1
      kv[evt.ke] = evt.val
    elif isinstance(evt, Get):
      oldv = kv[evt.ke]
      if oldv != resl:
        print tick, 'Expected', oldv, resl
        errors += 1
        # correct for the error
        kv[evt.ke] = resl
  return errors


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

