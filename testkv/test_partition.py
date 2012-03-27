

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, pretty_print, \
                    joint_print

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

kv['foo'] = '#1 : init'
kv2['foo'] = '#2 : init'

harn.network[serv] = False

kv['foo'] = '#1 : 0'
kv2['foo'] = '#2 : 0'
kv['foo'] = '#1 : 1'
kv2['foo'] = '#2: 1'
harn.network[serv] = True

kv['BREAK'] = 'BREAK_'
kv2['BREAK'] = 'BREAK'
kv['foo'] = '#1 : 2'
kv2['foo'] = '#2 : 2'
kv['foo']
kv2['foo']

harn.execute(CLOCK_RATE)


joint_print(cli.ctrace, cli2.ctrace)

errs = eval_strict_ordering(merge_traces(cli.ctrace, cli2.ctrace))

print "Ordering Errors: ", errs

harn.print_stats()


