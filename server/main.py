import db
import net
import sys

import traceback

from logger import log


def main(idx, master, addrs):
  log('main init with:' + str(addrs))
  d = db.Datastore()
  me = addrs[int(idx)]
  log('I am:' + str(me))
  log('master is:' + str(master))
  #print 'Starting as {0} as master? {1}'.format(me, master)
  n = net.Network(d, addrs, me, master)
  evtloop = net.EventLoop(n)
  evtloop.poll()

if len(sys.argv) <= 1:
  print "usage: main.py IDX host:port [host:port ...]"
  raise SystemExit

idx = int(sys.argv[1])

addrs = []
for a in sys.argv[2:]:
  l = a.split(':')
  addrs.append((l[0], int(l[1])))

master = '0'

sortd = sorted(addrs)
#print addrs, sortd
if addrs[idx] == sortd[0]:
  master = '1'

try:
  log('starting v2.0!')
  main(idx, master, addrs)
except Exception, e:
  log('ERROR')
  log(traceback.format_exc())
