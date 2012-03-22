


"""
Make a script for this to execute and make a script for
C library to execute
"""

from collections import namedtuple
from time import time
from cout import run_transcript, Init, Recover, Fail, Get, Put, \
                 ClientThread


PutEvent = namedtuple('Put', ['k', 'v'])
GetEvent = namedtuple('Get', ['k'])
NetKillEvent = namedtuple('NetKill', ['host0', 'host1'])
NetUpEvent = namedtuple('NetUp', ['host0', 'host1'])
HostKill = namedtuple('HostKill', ['host', 'port'])
HostUp = namedtuple('HostKill', ['host', 'port'])
FailEvent = namedtuple('Fail', ['host', 'port'])
RecoverEvent = namedtuple('Recover', ['host', 'port'])



def build_plan(sys, rate):
  myplan = []
  cplan = []
  
  # assume we start at 0
  ti = 0
  last_tick = 0
  sleep_ticks = 0
  clog = []
  plan = []
  

  msec_slack = 0
  for tick, evt in sys.xcript.log:
    if (tick - last_tick) > 1:
      # we have slack time
      msec_slack += rate * (tick - last_tick - 1)
    ti += (tick - last_tick) * rate
    last_tick = tick
    
    if isinstance(evt, Init):
      clog.append((ti, tick, evt))
    elif isinstance(evt, FailEvent):
      f = Fail('{0.host!s}:{0.port!s}'.format(evt))
      clog.append((ti, tick, f))
    elif isinstance(evt, RecoverEvent):
      e = Recover('{0.host!s}:{0.port!s}'.format(evt))
      clog.append((ti, tick, e))
    elif isinstance(evt, PutEvent):
      e = Put(evt.k, evt.v)
      clog.append((ti, tick, e))
    elif isinstance(evt, GetEvent):
      e = Get(evt.k)
      clog.append((ti, tick, e))
    else:
      # we always buffer events in the plan
      plan.append( (ti, evt) )
  # Add the termination step
  clog.append( (ti + rate, tick+1, None) )
  return ClientThread(clog), plan, msec_slack / 1000.0
    
  









