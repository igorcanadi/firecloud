

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from transcribe import build_plan
from cout import run_transcript, ClientThread
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors

clk = Clock()
xcript = Transcript(clk)


serv = Server(xcript, '192.168.56.101', '8808')
serv1= Server(xcript, '127.0.0.1', '8080')
serv2= Server(xcript, '127.0.0.1', '8888')
serv3= Server(xcript, '127.0.0.1', '9988')
network = Network([serv, serv1, serv2, serv3], xcript)

sys = Client(clk, [serv])


kv = sys.store

for i in xrange(50):
  kv['foo'] = 'bar' + str(i)
  kv['foo']




cli, plan, dead_time = build_plan(sys, CLOCK_RATE)

network[(serv, serv1)] = False

ignore, plan, dead_time = build_plan(network, CLOCK_RATE)

print plan

cli.start()

cli.join()

print 'Total Errors:', count_errors(cli.ctrace)

print 'Thread 1 ran for: run time={0}, dead_time={1} slack={2}'.format( cli.runtime, dead_time, cli.ctrace.slack)

effective_time = cli.runtime - cli.ctrace.slack

print 'C-Runtime (msec):', cli.ctrace.runtime

print 'effecitve run time (not sleeping), seconds: ', effective_time

print 'Mean Time per Request (ms): ', cli.runtime * 1000 / cli.ctrace.reqcount
print '(Effective) Mean Time per Request (ms): ', effective_time * 1000 / cli.ctrace.reqcount

print 'Slack % = {0}'.format(cli.ctrace.slack *1.0/ (cli.runtime - dead_time) * 100)




#print replay_gets_into_dict(cli.ctrace)

print 'strict ordering errors', eval_strict_ordering(cli.ctrace)
