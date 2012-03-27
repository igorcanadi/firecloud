

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, pretty_print, \
                    joint_print, replay_gets_into_dict

from time import time


from harness import create_harness
from actuator import hard_reset


hard_reset()


harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0x3, 0xC] )

serv = harn.servers[0]
serv1  = harn.servers[1]
serv2  = harn.servers[2]
serv3  = harn.servers[3]

kv = cli.store
kv2 = cli2.store

harn.network[(serv, serv2)] = False
harn.network[(serv, serv3)] = False
harn.network[(serv1, serv2)] = False
harn.network[(serv1, serv3)] = False

kv['parted'] = 'left : 0'
kv2['parted'] = 'right : 0'

kv['left'] = 'True'
kv2['right'] = 'True'

harn.network[(serv, serv2)] = True
harn.network[(serv, serv3)] = True
harn.network[(serv1, serv2)] = True
harn.network[(serv1, serv3)] = True

kv['right']
kv2['left']
kv['parted']
kv2['parted']


harn.execute(CLOCK_RATE)

joint_print(cli.ctrace, cli2.ctrace)

d0 = replay_gets_into_dict(cli.ctrace)
d1 = replay_gets_into_dict(cli2.ctrace)

errs = eval_strict_ordering(merge_traces(cli.ctrace, cli2.ctrace))

print "Ordering Errors (except !=0): ", errs

harn.print_stats()

print d0, d1

