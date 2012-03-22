

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors

from time import time


from harness import create_harness
from actuator import hard_reset

hard_reset()


harn = create_harness()

NUM_CLIENTS = 3

REQS = 2000

clients = [harn.client_by_mask( 0XF ) for x in xrange(NUM_CLIENTS)]

CLOCK_RATE = 0.5

for r in xrange(REQS/NUM_CLIENTS):
  for cl in clients:
    if r % 2 == 0:
      cl['foo'] = str(cl) + str(r)
    else:
      cl['foo']

start = time()
harn.execute(CLOCK_RATE)
end = time()

print 'Delta time (s): ', end - start
print 'Reqs / second: ', REQS * 1.0 / (end-start)


harn.print_stats()


