

fname = 'hist.dat'


bins = [0 for x in xrange(15)]

def bin(d):
  d = int(d)
  for x in xrange(15):
    if 300 * (2 ** x) > d:
      bins[x] += 1
      return
  print 'Failed:', d


with open(fname) as f:
  for l in f.readlines():
    bin(l)

for x in xrange(15):
  print '{0}ms : {1}'.format( (100 * (2 ** x) * 1.0 / 1000), bins[x])

