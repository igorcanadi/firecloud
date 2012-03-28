"""
Does things to the system according to a plan
created by transcribe
"""

from threading import Thread
from transcribe import HostKill, HostUp, NetKillEvent, NetUpEvent
from actuator import partition, partition_heal, \
                     take_server_down, bring_server_up


from time import time, sleep


def sleep_until(atime):
  delta = atime - time() 
  if delta < 0:
    raise Exception('Behind Schedule by {0}s'.format(delta))
  sleep(delta)




class ActThread(Thread):
  def __init__(self, tups):
    super(ActThread, self).__init__()
    self.abstime = None
    self.tups = tups

  def run(self):
    print 'Act Thread started.'
    start = self.abstime * 1.0 /1000
    for offset, act in self.tups:
      # offset is in msec
      sleep_until(offset * 1.0/1000 + start )
      self.take_action(act)
  
  def take_action(self, act):
    if isinstance(act, NetKillEvent):
      partition(act.host0.host, act.host1.host)
    elif isinstance(act, NetUpEvent):
      partition_heal(act.host0.host, act.host1.host)
    elif isinstance(act, HostKill):
      take_server_down(act.host, act.port)
    elif isinstance(act, HostUp):
      bring_server_up(act.host, act.port)
    else: 
      raise Exception("Bad Igor.")




