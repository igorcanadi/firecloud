


"""
Make a script for this to execute and make a script for
C library to execute
"""

from collections import namedtuple
from time import time
from cout import run_transcript, Init, Recover, Fail, Get, Put


PutEvent = namedtuple('Put', ['k', 'v'])
GetEvent = namedtuple('Get', ['k'])
NetKillEvent = namedtuple('NetKill', ['host0', 'host1'])
NetUpEvent = namedtuple('NetUp', ['host0', 'host1'])
HostKill = namedtuple('HostKill', ['host', 'port'])
HostUp = namedtuple('HostKill', ['host', 'port'])


COMMON_DELAY = 1000


def build_plan(sys, rate):
  myplan = []
  cplan = []
  
  # assume we start at 0
  ti = 0
  last_tick = 0
  sleep_ticks = 0
  clog = []
  plan = []
  
  #make the init
  clog.append((ti, 0, Init(map(str, sys.nodes))))
  ti += COMMON_DELAY * 2

  print "log length: ", len(sys.xcript.log)
  for tick, evt in sys.xcript.log:
    ti += (tick - last_tick) * rate
    last_tick = tick
    
    if isinstance(evt, HostKill):
      f = Fail('{0.host!s}:{0.port!s}'.format(evt))
      ti += COMMON_DELAY
      clog.append((ti, tick, f))
      plan.append((ti, evt))
      ti += COMMON_DELAY
    elif isinstance(evt, HostUp):
      e = Recover('{0.host!s}:{0.port!s}'.format(evt))
      ti += COMMON_DELAY
      clog.append((ti, tick, e))
      plan.append((ti, evt))
      ti += COMMON_DELAY
    elif isinstance(evt, PutEvent):
      e = Put(evt.k, evt.v)
      clog.append((ti, tick, e))
    elif isinstance(evt, GetEvent):
      e = Get(evt.k)
      clog.append((ti, tick, e))
    else:
      # we always buffer events in the plan
      ti += COMMON_DELAY
      plan.append( (ti, evt) )
      ti += COMMON_DELAY
  return clog, plan
    
  









