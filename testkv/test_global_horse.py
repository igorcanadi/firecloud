

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, \
                    pretty_print, eval_fuzzy_order

from time import time


from harness import create_harness
from actuator import hard_reset

from patterns import network_horse, network_allup

hard_reset()


harn = create_harness()

clients = harn.clients_by_masks( [0x1, 0x2, 0x4, 0x8] )


network_horse(harn)


ROUNDS = 100

for r in xrange(ROUNDS):
  for i, c in enumerate(clients):
    c.store['ke'] = '{0} {1}'.format(i, r)

harn.execute(CLOCK_RATE)

m = reduce(merge_traces, map(lambda x: x.ctrace, clients))

pretty_print(m)

errs = eval_strict_ordering(m)


print "Ordering Errors: ", errs

print "Has fuzzy order?", eval_fuzzy_order(m)

harn.print_stats()


