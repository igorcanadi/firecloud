

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from transcribe import build_plan
from cout import run_transcript, ClientThread
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering

clk = Clock()
xcript = Transcript(clk)


serv = Server(xcript, '127.0.0.1', '1234')
serv1= Server(xcript, '127.0.0.1', '8080')
serv2= Server(xcript, '127.0.0.1', '8888')
serv3= Server(xcript, '127.0.0.1', '9988')
network = Network([serv, serv1, serv2, serv3], xcript)

sys = Client(clk, [serv1])


kv = sys.store

for i in xrange(100):
  kv['foo'] = 'bar'
  kv['foo___'+str(i)]




cli, plan, dead_time = build_plan(sys, CLOCK_RATE)

cli.start()

cli.join()


print 'Thread 1 ran for: run time={0}, dead_time={1} slack={2}'.format( cli.runtime, dead_time, cli.ctrace.slack)

print 'Slack % = {0}'.format(cli.ctrace.slack *1.0/ (cli.runtime - dead_time) * 100)




#print replay_gets_into_dict(cli.ctrace)

print 'cli errors', eval_strict_ordering(cli.ctrace)
