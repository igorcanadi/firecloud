

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, \
                    joint_print
                    

from time import time


from harness import create_harness
from actuator import hard_reset

hard_reset()

harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0xF, 0xF] )

serv = harn.servers[0]
serv1  = harn.servers[1]
serv2  = harn.servers[2]
serv3  = harn.servers[3]

cli.fail(serv1)
cli.fail(serv3)
cli.fail(serv2)

cli2.fail(serv2)
cli2.fail(serv3)
cli2.fail(serv)

kv = cli.store
kv2 = cli2.store

kv['foo'] = 'A 0'
kv2['foo'] = 'B 0'
harn.network[serv] = False
kv['foo'] = 'A 1'
kv2['foo'] = 'B 1'
kv['foo'] = 'A 2'
kv2['foo'] = 'B 2'
harn.network[serv] = True
kv['foo'] = 'A 3'
kv2['foo'] = 'B 3'


harn.execute(CLOCK_RATE)

joint_print(cli.ctrace, cli2.ctrace)


harn.print_stats()


