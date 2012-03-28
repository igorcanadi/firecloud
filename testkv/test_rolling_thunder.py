

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

cli, = harn.clients_by_masks( [0x1] )


ROUNDS = 2
SETS = 100
count = 0

harn.fail(harn.servers[0])

for r in xrange(ROUNDS):
  for sno in xrange(4):
    for s in xrange(SETS):
      cli.store['ke{0}'.format(count)] = str(count)
      count += 1

    ts = (sno+1) % 4 
    harn.servers[ts].fail()
    if ts == 0:
      cli.fail(harn.servers[ts])

    ts = sno% 4 
    harn.servers[ts].recover()
    if ts == 0:
      cli.recover(harn.servers[ts])



harn.recover(harn.servers[0])

for r in xrange(count):
  cli.store['ke{0}'.format(r)]

harn.execute(CLOCK_RATE)


errs = eval_strict_ordering(cli.ctrace)


pretty_print(cli.ctrace)
print "Ordering Errors: ", errs


harn.print_stats()


