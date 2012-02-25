

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from transcribe import build_plan
from cout import run_transcript, ClientThread
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering

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
  kv['foo___'+str(i)]

kv2['foo_MEGA'] = 'bar'
for i in xrange(10):
  print 'DOING IT CORRECTLY!'
  kv2['foo' + str(i)] = str(i) + 'foobar'
  kv2['foo_?_' + str(i)]

for i in xrange(10):
  clk.tick()
  kv['foo'+str(i)] = 'bar_' + str(i)
  clk.tick()
  kv['foo'+str(i)]

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




print replay_gets_into_dict(cli.ctrace)
print replay_gets_into_dict(cli2.ctrace)

print 'merging'

merged = merge_traces(cli.ctrace, cli2.ctrace)
print replay_gets_into_dict(merged.trace)


print 'cli errors', eval_strict_ordering(cli.ctrace)
print 'cli2 errors', eval_strict_ordering(cli2.ctrace)

print "merged errors", eval_strict_ordering(merged)

