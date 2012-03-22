

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors

from time import time


from harness import create_harness


harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0x1, 0x2] )

serv = harn.servers[0]
serv1  = harn.servers[1]

kv = cli.store
kv2 = cli2.store

kv['foo'] = 'var'

kv2['foo'] = 'var2'

harn.network[serv] = False
kv['foo'] = 'var'
kv2['foo'] = 'var2'
kv['foo'] = 'var'
kv2['foo'] = 'var2'
harn.network[serv] = True
kv['foo'] = 'var'
kv2['foo'] = 'var2'


harn.execute(10)


harn.print_stats()


