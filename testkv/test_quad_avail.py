

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, \
                    pretty_print

from time import time


from harness import create_harness
from actuator import hard_reset

from patterns import network_horse, network_allup, network_quad

hard_reset()


harn = create_harness()

clients = harn.clients_by_masks( [0x1, 0x2, 0x4, 0x8] )


network_quad(harn)


ROUNDS = 20

for r in xrange(ROUNDS):
  for i, c in enumerate(clients):
    c.store['key'] = '{0}.{1}'.format(i, r)

harn.execute(CLOCK_RATE)

harn.print_stats()

for i, c in enumerate(clients):
  er = eval_strict_ordering(c.ctrace)
  print "Client #{0} errors: {1}".format(i, er)



m = reduce(merge_traces, map(lambda x: x.ctrace, clients))
errs = eval_strict_ordering(m, False)

print 'How consistent? ', (1 - errs * 1.0 / (4 * ROUNDS)) * 100, '%'
