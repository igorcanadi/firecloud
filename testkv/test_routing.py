

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, pretty_print, \
                    joint_print, replay_gets_into_dict

from time import time


from harness import create_harness
from actuator import hard_reset


hard_reset()


harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0x1, 0x2] )

serv = harn.servers[0]
serv1  = harn.servers[1]
serv2  = harn.servers[2]
serv3  = harn.servers[3]

kv = cli.store
kv2 = cli2.store

harn.network[(serv, serv1)] = False

kv['parted'] = '#1 : 0'
kv2['parted'] = '#2 : 0'

kv['joint'] = '#1 : 1'
kv2['joint'] = '#2 : 1'

kv['joint2'] = '#1 : 2'
kv2['join2'] = '#2 : 2'

kv['parted']
kv2['parted']

harn.network[(serv, serv1)] = True

kv['joint']
kv2['joint']

for i in xrange(50):
  harn.clock.tick()


kv['joint2']
kv2['joint2']


harn.execute(CLOCK_RATE)

joint_print(cli.ctrace, cli2.ctrace)

d0 = replay_gets_into_dict(cli.ctrace)
d1 = replay_gets_into_dict(cli2.ctrace)

errs = eval_strict_ordering(merge_traces(cli.ctrace, cli2.ctrace))

print "Ordering Errors (except !=0): ", errs

harn.print_stats()

print 'Consistent when partitioned? [{0}] {1}'.format(d0['parted'], d0['parted'] == d1['parted'])
print 'Consistent immediately after join? [{0}] {1}'.format(d0['joint'], d0['joint'] == d1['joint'])
print 'Consistent after a while? [{0}] {1}'.format(d0['joint2'], d0['joint2'] == d1['joint2'])


print '** Has Routing? {0}'.format(d0['parted'] == d1['parted'])
