"""
Does things to the system according to a plan
created by transcribe
"""

from threading import Thread
from transcribe import HostKill, HostUp, NetKillEvent, NetUpEvent

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
    start = self.abstime * 1.0 /1000
    for offset, act in self.tups:
      # offset is in msec
      sleep_until(offset * 1.0/1000 + start )
      self.take_action(act)
  
  def take_action(self, act):
    print 'Doing Action: act'
