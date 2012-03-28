

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

KEYS = 200

harn.network[(serv, serv1)] = False

for k in xrange(KEYS):
  kv['A1 %s'%k] = 'A_%s' % k
  kv2['B1 %s'%k] = 'B_%s' % k

for k in xrange(KEYS):
  kv['A2 %s'%k] = 'A2 %s' % k
  kv2['A1 %s'%k]
  kv['B1 %s'%k]
  kv2['B2 %s'%k] = 'B2 %s' % k

harn.network[(serv, serv1)] = True

for k in xrange(KEYS):
  kv['B2 %s'%k]
  kv2['A2 %s'%k]


harn.execute(CLOCK_RATE)

d0 = replay_gets_into_dict(cli.ctrace)
d1 = replay_gets_into_dict(cli2.ctrace)

while_sep = 0
together = 0
for k in xrange(KEYS):
  if d1['A1 %s'%k] != '[A_%s]' % k:
    while_sep += 1
  if d0['B1 %s'%k] != '[B_%s]' % k:
    while_sep += 1
  
  if d1['A1 %s'%k] != '[A %s]' % k:
    together += 1
  if d0['B1 %s'%k] != '[B %s]' % k:
    together += 1

harn.print_stats()

print 'Missing when seperated: ', while_sep
print 'Missing when together: ', together
