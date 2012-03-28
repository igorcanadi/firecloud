

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, \
                    pretty_print

from time import time


from harness import create_harness
from actuator import hard_reset

from patterns import network_quad

hard_reset()


harn = create_harness()

REQS = 500

cli = harn.client_by_mask(0xF)

network_quad(harn)


for r in xrange(REQS):
  cli['ke'+str(r)] = r
  cli[str(r) + 'ke'] = r
  cli['ke'+str(r)]
  cli[str(r) + 'ke']

start = time()
harn.execute(CLOCK_RATE)
end = time()

print 'Delta time (s): ', end - start
print 'Reqs / second: ', REQS * 1.0 / (end-start)


harn.print_stats()

print 'Strict Ordering: ', eval_strict_ordering(cli.ctrace)

#pretty_print(cli.ctrace)

