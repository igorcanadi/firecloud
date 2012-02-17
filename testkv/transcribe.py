


"""
Make a script for this to execute and make a script for
C library to execute
"""

from collections import namedtuple
from time import time


PutEvent = namedtuple('Put', ['k', 'v', 'oldv'])
GetEvent = namedtuple('Get', ['k', 'v'])
NetKillEvent = namedtuple('NetKill', ['host0', 'host1'])
NetUpEvent = namedtuple('NetUp', ['host0', 'host1'])
SleepEvent = namedtuple('Sleep', ['msec'])
HostKill = namedtuple('HostKill', ['host', 'port'])
HostUp = namedtuple('HostKill', ['host', 'port'])



def build_plan(xcript, rate):
  myplan = []
  cplan = []
  
  # assume we start at 0
  last_tick = 0
  sleep_ticks = 0
  for tick, evt in xcript.log:
    if last_tick + 1 != tick:
      # we have to sleep for the difference
      rate * 
      continue
    if type(evt)









