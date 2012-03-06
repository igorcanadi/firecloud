import db
import net
import sys


def main(idx, master, addrs):
  d = db.Datastore()
  me = addrs[int(idx)]
  n = net.Network(d, addrs, me, master)
  n.poll()

idx = int(sys.argv[1])
master = int(sys.argv[2])

addrs = []
for a in sys.argv[3:]:
  l = a.split(':')
  addrs.append((l[0], int(l[1])))

main(idx, master, addrs)
