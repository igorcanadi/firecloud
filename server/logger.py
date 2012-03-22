
from time import time

LOG_FILE = open('/tmp/server.log', 'a')
VERBOSE = 0

def barf(txt):
  if not '\n' in txt:
    txt += '\n'
  LOG_FILE.write('BARF: %s : %s' % (time(), txt)) 

def log(txt):
  if VERBOSE:
      if not '\n' in txt:
        txt += '\n'
      LOG_FILE.write('%s : %s' % (time(), txt))

