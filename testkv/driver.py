

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from transcribe import build_plan
from cout import run_transcript, ClientThread
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering

clk = Clock()
xcript = Transcript(clk)


serv = Server(xcript, 'localhost', '1234')
network = Network([serv, serv2], xcript)

sys = Client(clk, [serv, serv2])


kv = sys.store

for i in xrange(10):
  kv['foo'] = 'bar'
  kv['foo___'+str(i)]

for i in xrange(10):
  clk.tick()
  kv['foo'+str(i)] = 'bar_' + str(i)
  clk.tick()
  kv['foo'+str(i)]



cli, plan, dead_time = build_plan(sys, CLOCK_RATE)

cli.start()

cli.join()


print 'Thread 1 ran for: ', cli.runtime, dead_time, cli.slack




print replay_gets_into_dict(cli.ctrace)

print 'cli errors', eval_strict_ordering(cli.ctrace)
