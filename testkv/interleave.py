

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from transcribe import build_plan
from cout import run_transcript, ClientThread
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors

clk = Clock()
xcript = Transcript(clk)


serv = Server(xcript, '192.168.56.101', '8808')
serv1 = Server(xcript, '192.168.56.102', '8808')
network = Network([serv, serv1], xcript)

sys = Client(clk, [serv])
sys2 = Client(clk, [serv1])


kv = sys.store
kv2 = sys2.store

for i in xrange(2):
  kv['foo'] = 'bar'
  kv2['foo']
  kv2['foo'] = 'bar2'
  kv['foo']
  




cli, plan, dead_time = build_plan(sys, CLOCK_RATE)
cli2, plan2, dead_time2 = build_plan(sys2, CLOCK_RATE)

cli.start()
cli2.start()

cli.join()
cli2.join()

print 'Total Errors:', count_errors(cli.ctrace)

print 'Thread 1 ran for: run time={0}, dead_time={1} slack={2}'.format( cli.runtime, dead_time, cli.ctrace.slack)

effective_time = cli.runtime - cli.ctrace.slack

print 'C-Runtime (msec):', cli.ctrace.runtime

print 'effecitve run time (not sleeping), seconds: ', effective_time

print 'Mean Time per Request (ms): ', cli.runtime * 1000 / cli.ctrace.reqcount
print '(Effective) Mean Time per Request (ms): ', effective_time * 1000 / cli.ctrace.reqcount

print 'Slack % = {0}'.format(cli.ctrace.slack *1.0/ (cli.runtime - dead_time) * 100)

print 'strict ordering errors cli1', eval_strict_ordering(cli.ctrace)

mrg = merge_traces(cli.ctrace, cli2.ctrace)

print 'ORDERING:'
for tick, ti, evt, resl in mrg.trace:
  print '%-5s %40s %20s' % (tick, evt, resl)


print 'strict ordering errors merged', eval_strict_ordering(mrg)


#print replay_gets_into_dict(cli.ctrace)

print 'strict ordering errors', eval_strict_ordering(cli.ctrace)
