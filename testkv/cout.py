
from struct import pack
from collections import namedtuple
from subprocess import Popen, PIPE, STDOUT
import time as time_
from conf import SYNC_WINDOW 
from threading import Thread

ERROR_CODE = 0xDEADBEEF

class ClientTrace(object):
  def __init__(self, trace, slack, reqcount, runtime):
    self.slack = slack
    self.trace = trace
    self.reqcount = reqcount
    self.runtime = runtime

  def __iter__(self):
    return self.trace.__iter__()

"""
void kv739_init(char *servers[]) - provide a null-terminated list of servers in the format "host:port" and initialize the client code. Returns 0 on success and -1 on failure.
void kv739_fail(char * server) - indicate that the server "host:port" has failed and the client should not attempt to contact it. This is a simple way to partition clients from servers.
void kv739_recover(char * server) - indicate that the server "host:port" has recovered and the client can contact it again.
int kv739_get(char * key, char * value) - retrieve the value corresponding to the key. If the key is present, it should return 0 and store the value in the provided string. The string must be at least 1 byte larger than the maximum allowed value. If the key is not present, it should return 1. If there is a failure, it should return -1.
int kv739_put(char * key, char * value, char * old_value) - Perform a get operation on the current value into old_value and then store the specified value. Should return 0 on success if there is an old value, 1 on success if there was no old value, and -1 on failure. The old_value parameter must be at least one byte larger than the maximum value size.
"""

"""
void kv739_init(char *servers[])
void kv739_fail(char * server)
void kv739_recover(char * server)
int kv739_put(char * key, char * value, char * old_value)
int kv739_get(char * key, char * value)
"""


Init = namedtuple('Init', 'servers')
Recover = namedtuple('Recover', 'serv')
Fail = namedtuple('Fail', 'serv')
Put = namedtuple('Put', ['ke', 'val'])
Get = namedtuple('Get', 'ke')

codes = {
  Init : 0,
  Recover : 2,
  Fail : 1,
  Get : 3,
  Put : 4,
  type(None): 99
    }

#
# Packings
#


HEADER = 'QQQQ'


def pad(st):
  while len(st) < 254:
    st += '\0'
  return st

def pad_key(ke):
  while len(ke) < 128:
    ke = ke + '\0'
  return ke

class Buffer_(object):
  def __init__(self):
    self.buf = ''

  def write(self, msg):
    self.buf = self.buf + msg


class ClientThread(Thread):
  def __init__(self, tups):
    super(ClientThread, self).__init__()
    self.tups = tups
    self.log = None
    self.slack = None
    self.abstime = None

  def run(self):
    start = time_.time()
    assert self.abstime is not None
    self.ctrace = run_transcript(self.tups, self.abstime)
    self.slow_runtime = time_.time() - start
    self.runtime = self.ctrace.runtime




def write_out(abstime, time, seq, itm, out):
  data = 0
  if type(itm) == Put:
    data = len(itm.val) + 1 # for the null
  elif type(itm) == Init:
    #print 'Doing init -------------'
    data = len(itm.servers)
    time = abstime
  #print "Seq #%s scheduled for %s" % (seq, time)
  head = pack(HEADER, time, seq, codes[type(itm)], data)
  #print 'Built header for: ', codes[type(itm)]
  out(head)
  
  if type(itm) == Init:
    for srv in itm.servers:
      out(pad(srv))
      out('\0')
  if type(itm) == Recover:
    out(pad(itm.serv))
    out('\0')
  if type(itm) == Fail:
    out(pad(itm.serv))
    out('\0')
  if type(itm) == Put:
    out(pad_key(itm.ke))
    out('\0')
    out(itm.val)
    out('\0')
  if type(itm) == Get:
    out(pad_key(itm.ke))
    out('\0')


def run_transcript(tups, abstime):
  buf = Buffer_()
  for ti, tick, evt in tups:
    write_out(abstime, int(ti), tick, evt, buf.write)
  p = Popen(['./runner'], stdin=PIPE, stderr=STDOUT, stdout=PIPE)
  with open('raw_transcript', 'w') as f:
    f.write(buf.buf)
  out, err = p.communicate(input=buf.buf)
  return reconstruct(out, tups)

def fake_run_transcript(tups):
  d = {}
  l = []
  for ti, tick, evt in tups:
    if isinstance(evt, Get):
      oldv = ''
      if evt.ke in d:
        oldv = d[evt.ke]
      l.append( (tick, ti, evt, '['+str(oldv)+ ']') )
    elif isinstance(evt, Put):
      oldv = ''
      if evt.ke in d:
        oldv = d[evt.ke]
      d[evt.ke] = evt.val
      l.append( (tick, ti, evt, '['+str(oldv)+ ']' ) )
  return ClientTrace(l, 0)


def reconstruct(text, tups):
  tickmap = dict([(tick, evt) for ti, tick, evt in tups])
  construct = []
  usec_slack = 0
  reqcount = 0
  first_time_stamp = None
  last_time_stamp = None
  for line in text.split('\n'):
    if len(line) == 0 or line[0] != '+':
      continue
    # ignore leading '+ '
    line = line[2:]
    line.lstrip(' ')
    i = line.index(' ')
    tick, txt = line[0:i], line[i+1:]
    tick = int(tick)
    if tick == -1:
      # THere was an error
      raise Exception(txt)
    elif tick == -2:
      usec_slack += int(txt)
    else:
      reqcount += 1
      # Handle a GET or PUT
      i = txt.index(' ')
      msec, txt= txt[0:i], txt[i+1:]
      msec = int(msec) / 1000.0
      if first_time_stamp is None:
        first_time_stamp = msec
      last_time_stamp = msec
      i = txt.index(' ')
      code, txt= txt[0:i], txt[i+1:]
      code = int(code)
      if code == 0:
        # worked correctly
        pass
      elif code < 0:
        # error occured
        txt = None
      elif code > 0:
        # no previous key
        txt = '[]'
      construct.append((tick, msec, tickmap[tick], txt))
  return ClientTrace(construct, usec_slack/ (1000.0 * 1000.0), reqcount, last_time_stamp-first_time_stamp)

#run_transcript( [(0, 0, Init(['localhost:8080']))] )

