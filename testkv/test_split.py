

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors

from time import time


from harness import create_harness
from actuator import hard_reset

hard_reset()


harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0x3, 0xC] )

serv = harn.servers[0]
serv1  = harn.servers[1]
serv2= harn.servers[2]
serv3  = harn.servers[3]

kv = cli.store
kv2 = cli2.store

harn.network[(serv, serv2)] = False
harn.network[(serv, serv3)] = False

harn.network[(serv1, serv2)] = False
harn.network[(serv1, serv3)] = False



for i in xrange(10):
  kv['foo'] = 'var' + str(i)
  kv2['foo'] = 'var_' + str(i)

harn.network[(serv, serv2)] = True
harn.network[(serv, serv3)] = True

harn.network[(serv1, serv2)] = True
harn.network[(serv1, serv3)] = True

for i in xrange(10):
  kv['foo'] = 'var' + str(i)
  kv2['foo'] = 'var_' + str(i)


harn.execute(CLOCK_RATE)


harn.print_stats()


