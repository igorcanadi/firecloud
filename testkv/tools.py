
from random import random, choice





CHARS = [chr(x) for x in xrange(0x20, 0x7E+1)]
# Remove `[' and `]' because people are too lazy to escape
CHARS.remove('[')
CHARS.remove(']')


SMALL_LEN = 10
BIG_LEN = 500
VERY_BIG_LEN = 50000




def make_str(l):
  s = ''
  for n in xrange(l):
    s += choice(CHARS)
  return s



