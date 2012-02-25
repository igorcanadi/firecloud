

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from transcribe import build_plan
from cout import run_transcript, ClientThread

clk = Clock()
xcript = Transcript(clk)


serv = Server(xcript, 'localhost', '1234')
serv2 = Server(xcript, 'localhost', '1235')
network = Network([serv, serv2], xcript)

sys = Client(clk, [serv, serv2])
sys2 = Client(clk, [serv, serv2])


kv = sys.store

kv2 = sys2.store

for i in xrange(10):
  kv['foo'] = 'bar'
  kv['foo']

kv2['foo'] = 'bar'
for i in xrange(10):
  kv2['foo']

for i in xrange(10):
  clk.tick()
  kv['foo'] = 'bar'
  clk.tick()
  kv['foo']

serv.fail()

network[(serv, serv2)] = False

serv.recover()

kv['foo'] = 'bar'
kv['foo']
network[(serv2, serv)] = True


cli, plan, dead_time = build_plan(sys, CLOCK_RATE)
cli2, plan2, dead_time2 = build_plan(sys2, CLOCK_RATE)

cli.start()
print 'Started CLI'
cli2.start()

cli.join()
cli2.join()


print 'Thread 1 ran for: ', cli.runtime, dead_time, cli.slack
print 'Thread 2 ran for: ', cli2.runtime, dead_time2, cli2.slack


print cli.log

