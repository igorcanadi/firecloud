
from time import time

LOG_FILE = '/tmp/server.log'

def log(txt):
  if not '\n' in txt:
    txt += '\n'
  with open(LOG_FILE, 'a') as f:
    f.write('%s : %s' % (time(), txt))

