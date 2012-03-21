
from time import time

LOG_FILE = '/tmp/server.log'
VERBOSE = 1

def log(txt):
  if VERBOSE:
      if not '\n' in txt:
        txt += '\n'
      with open(LOG_FILE, 'a') as f:
        f.write('%s : %s' % (time(), txt))

