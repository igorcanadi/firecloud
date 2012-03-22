

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from transcribe import build_plan
from cout import run_transcript, ClientThread
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors
from acthread import ActThread

from time import time

clk = Clock()
xcript = Transcript(clk)


serv = Server(xcript, '192.168.56.103', '8808')
serv1 = Server(xcript, '192.168.56.104', '8808')
network = Network([serv, serv1], xcript)


sys = Client(clk, [serv])
sys2 = Client(clk, [serv1])


kv = sys.store
kv2 = sys2.store



for i in xrange(20):
  kv['foo'] = 'bar' + str(i)
  serv.fail()
  kv2['foo']
  serv.recover()
  network[(serv, serv1)] = False
  kv2['foo'] = 'bar_' + str(i)
  kv['foo']
  



cli, plan, dead_time = build_plan(sys, CLOCK_RATE)
cli2, plan2, dead_time2 = build_plan(sys2, CLOCK_RATE)

ignore, plan, dead_time = build_plan(network, CLOCK_RATE)

ctl = ActThread(plan)


strt = (time() * 1000) + 1000


cli.abstime = strt
cli2.abstime = strt
ctl.abstime = strt

ctl.start()
cli.start()
cli2.start()

cli.join()
cli2.join()
ctl.join()

print 'Total Errors:', count_errors(cli.ctrace)

print 'Thread 1 ran for: run time={0}, dead_time={1} slack={2}'.format( cli.runtime, dead_time, cli.ctrace.slack)

effective_time = cli.ctrace.slack

print 'C-Runtime (msec):', cli.ctrace.runtime

print 'effecitve run time (not sleeping), seconds: ', effective_time

print 'Mean Time per Request (ms): ', cli.runtime * 1000 / cli.ctrace.reqcount
print '(Effective) Mean Time per Request (ms): ', effective_time * 1000 / cli.ctrace.reqcount

mrg = merge_traces(cli.ctrace, cli2.ctrace)

print 'ORDERING:'
for tick, ti, evt, resl in mrg.trace:
  print '%-5s %40s %20s' % (tick, evt, resl)


print 'strict ordering errors merged', eval_strict_ordering(mrg)


#print replay_gets_into_dict(cli.ctrace)

