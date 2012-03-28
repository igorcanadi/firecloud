

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, pretty_print, \
                    joint_print, eval_fuzzy_order, eval_fuzzy_order_by_key

from time import time


from harness import create_harness
from actuator import hard_reset


hard_reset()

ROUNDS = 50
KEYS = 40

harn = create_harness()

clients = harn.clients_by_masks( [0xF, 0xF] )

for r in xrange(ROUNDS):
  for i, c in enumerate(clients):
    for ke in xrange(KEYS):
      c.store['ke{0}'.format(ke)] = '{0} {1}'.format(i, r)


harn.execute(CLOCK_RATE)

harn.print_stats()

m = reduce(merge_traces, map(lambda x: x.ctrace, clients))

errs = eval_strict_ordering(m)


print "Ordering Errors: ", errs

fo = eval_fuzzy_order_by_key(m)
ok = True
print 'Has ordering per-key?'
for k in sorted(fo):
  ok = ok and fo[k]
  print ' {0} : {1}'.format(k, fo[k])

print 'Has total ordering?', ok


