

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors

from time import time


from harness import create_harness
from actuator import hard_reset

hard_reset()

CLOCK_RATE = 300

harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0xF, 0xF] )

serv = harn.servers[0]
serv1  = harn.servers[1]
serv2  = harn.servers[2]
serv3  = harn.servers[3]

print serv, serv1, serv2, serv3
cli.fail(serv1)
cli.fail(serv3)
#cli.fail(serv2)

#cli2.fail(serv2)
#cli2.fail(serv3)
cli2.fail(serv)

kv = cli.store
kv2 = cli2.store

kv['foo'] = 'var'
kv2['foo'] = 'var2'

kv['foo'] = 'var__2'
kv2['foo'] = 'var_2'
kv['foo'] = 'var__3'
kv2['foo'] = 'var_3'
#harn.network[serv] = True
kv['foo'] = 'var__4'
kv2['foo'] = 'var_4'


harn.execute(CLOCK_RATE)


harn.print_stats()


