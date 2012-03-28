

from framework import Client, Server, Clock, Transcript, Network, CLOCK_RATE
from analysis import replay_gets_into_dict, merge_traces, \
                    eval_strict_ordering, count_errors, \
                    joint_print
                    

from time import time


from harness import create_harness
from actuator import hard_reset

hard_reset()

harn = create_harness()

cli, cli2 = harn.clients_by_masks( [0xF, 0x8] )

serv = harn.servers[0]
serv1  = harn.servers[1]
serv2  = harn.servers[2]
serv3  = harn.servers[3]

cli2.fail(serv2)
cli2.fail(serv3)
cli2.fail(serv)

kv = cli.store
kv2 = cli2.store

harn.fail(serv3)

KEYS = 1000

myd = {}
for k in xrange(KEYS):
  cli.store[str(k)] = str(k * k)
  myd[str(k)] = str(k*k)

harn.recover(serv3)

for k in xrange(KEYS):
  cli2.store[str(k)]

harn.execute(CLOCK_RATE)

d = replay_gets_into_dict(cli2.ctrace)

harn.print_stats()

errs = 0
for ke in myd:
  if (ke not in d) or ('[%s]' % myd[ke] != d[ke]):
    print 'expected: ', myd[ke], 'got: ', d[ke]
    errs += 1

print 'Consitency errors: %s / %s' % (errs, KEYS)




