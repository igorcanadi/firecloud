

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, pretty_print, \
                    joint_print, eval_fuzzy_order

from time import time


from harness import create_harness
from actuator import hard_reset


hard_reset()


harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0x1, 0x2] )

serv = harn.servers[0]
serv1  = harn.servers[1]

kv = cli.store
kv2 = cli2.store

kv['foo'] = '#1 0'
kv2['foo'] = '#2 1'

harn.network[serv] = False

kv['foo'] = '#1 2'
kv2['foo'] = '#2 3'
kv['foo'] = '#1 4'
kv2['foo'] = '#2 5'
harn.network[serv] = True

kv['foo'] = '#1 : 6'
kv2['foo'] = '#2 : 7'
kv['foo']
kv2['foo']

harn.execute(CLOCK_RATE)


joint_print(cli.ctrace, cli2.ctrace)

m =merge_traces(cli.ctrace, cli2.ctrace)


errs = eval_strict_ordering(m)

print "Ordering Errors: ", errs

fo = eval_fuzzy_order(m)
print 'Fuzzy ordering?', fo

harn.print_stats()


