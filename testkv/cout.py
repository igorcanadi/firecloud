
from struct import pack

"""
void kv739_init(char *servers[]) - provide a null-terminated list of servers in the format "host:port" and initialize the client code. Returns 0 on success and -1 on failure.
void kv739_fail(char * server) - indicate that the server "host:port" has failed and the client should not attempt to contact it. This is a simple way to partition clients from servers.
void kv739_recover(char * server) - indicate that the server "host:port" has recovered and the client can contact it again.
int kv739_get(char * key, char * value) - retrieve the value corresponding to the key. If the key is present, it should return 0 and store the value in the provided string. The string must be at least 1 byte larger than the maximum allowed value. If the key is not present, it should return 1. If there is a failure, it should return -1.
int kv739_put(char * key, char * value, char * old_value) - Perform a get operation on the current value into old_value and then store the specified value. Should return 0 on success if there is an old value, 1 on success if there was no old value, and -1 on failure. The old_value parameter must be at least one byte larger than the maximum value size.
"""

void kv739_init(char *servers[])
void kv739_fail(char * server)
void kv739_recover(char * server)
int kv739_put(char * key, char * value, char * old_value)
int kv739_get(char * key, char * value)


Init = namedtuple('Init', 'servers')
Recover = namedtuple('Recover', 'serv')
Fail = namedtuple('Fail', 'serv')
Put = namedtuple('Put', 'ke', 'val')
Get = namedtuple('Get', 'ke')
Sleep = namedtuple('Sleep', 'msec')


#
# Packings
#


HEADER = 'QQQ'


def pad(st):
  while len(st) < 254:
    ke += '\0'

def pad_key(ke):
  while len(ke) < 128:
    ke += '\0'


def write_out(time, seq, itm, out):
  data = 0
  if type(out) == Put:
    data = len(out.val) + 1 # for the null
  head = pack(HEADER, time, seq, data)
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



