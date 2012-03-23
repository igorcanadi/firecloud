

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors

from time import time


from harness import create_harness
from actuator import hard_reset

hard_reset()


harn = create_harness()

NUM_CLIENTS = 4

REQS = 1000

cli = harn.client_by_mask(0xF)

CLOCK_RATE = 3

for r in xrange(REQS/2):
  cli['foo'] = r
  cli['foo']

start = time()
harn.execute(CLOCK_RATE)
end = time()

print 'Delta time (s): ', end - start
print 'Reqs / second: ', REQS * 1.0 / (end-start)

print 'Strict Ordering: ', eval_strict_ordering(cli.ctrace)

harn.print_stats()


