

from framework import System, Server, Clock
from transcribe import build_plan
from cout import run_transcript

clk = Clock()
serv = Server('localhost', '1234')
serv2 = Server('localhost', '1235')

sys = System(clk, [serv, serv2])

kv = sys.store

kv['foo'] = 'bar'
kv['foo']

serv.fail()

sys.network[(serv, serv2)] = False

serv.recover()

kv['foo'] = 'bar'
kv['foo']
sys.network[(serv2, serv)] = True


clog, plan = build_plan(sys, 100)
print 'Clog:'
for i in clog:
  print i
print 'Plan:'
for i in plan:
  print i


print 'running...'
run_transcript(clog)
