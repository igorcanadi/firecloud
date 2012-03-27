"""
Actuates commands in the test system


The 'host' variable is always some string that you can shove
into the sock's connect method to get get a connection.

REQUIREMENT: id_rsa in current directory
"""
import subprocess

from os import system
from os import chdir
from conf import server_list
from time import sleep

RESET_DELAY = 0.4

def remote_exec(gate, cmd):
  #retval = subprocess.call(command, shell=True)
  #if retval != 0:
  #    return retval
  print 'ssh -i ../keys/id_rsa -p 22 user739@{0[0]} \"{1}\" &'.format(gate, cmd)
  system('ssh -i ../keys/id_rsa -p 22 user739@{0[0]} \"{1}\" &'.format(gate, cmd))

def partition(host1, host2):
  """ Creates a partition between the server at host1:port1 and 
  the server at host2:port2
  The partition should block all traffic between these two servers
  (even on ports other than port1 and port2), but should not
  block traffic between any other pair of servers
  @type host1: str
  @param host1: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port1: int
  @param host2: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port2: int
  @returns 0 on OK, non-0 on PANIC
  """
  c = './partition.sh -A {0} {1}'.format(host1, host2)
  print c
  chdir('..')
  assert system(c) == 0
  chdir('testkv')



def partition_heal(host1, host2):
  """ Removes any partition between the two servers. 
  After calling this, the server at host1:port1 and the 
  server at host2:port2 should be able to communicate fully
  on all ports. 
  @type host1: str
  @param host1: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port1: int
  @param host2: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port2: int
  @returns 0 on OK, non-0 on PANIC
  """
  chdir('..')
  c = './partition.sh -D {0} {1}'.format(host1, host2)
  print c
  assert system(c) == 0
  chdir('testkv')


# kill `lsof | grep 10000 | awk '{print $2}'`
def take_server_down(host, port=None):
  """ Takes the server down / kills the process / kills the VM.
  Implement this only if Swift says we need it
  @type host: str
  @param host: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port: int
  @returns 0 on OK, non-0 on PANIC
  """
  #command = "kill `lsof | grep %s | awk '{print $2}'`" % (port)
  command = "killall python 2>/dev/null"
  remote_exec((host, 22), command)


# kill `lsof | grep 10000 | awk '{print $2}'`
def flush_iptables(host):
  """ Takes the server down / kills the process / kills the VM.
  Implement this only if Swift says we need it
  @type host: str
  @param host: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port: int
  @returns 0 on OK, non-0 on PANIC
  """
  #command = "kill `lsof | grep %s | awk '{print $2}'`" % (port)
  command = "sudo iptables --flush"
  remote_exec((host, 22), command)


# requirement: main.py in the home directory on the server
def bring_server_up(host, port):
  """ Undo-what ever take_server_down does, so that the server works again
  Implement this only if Swift says we need it
  @type host: str
  @param host: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port: int
  @param hosts list of strs in format 'host:port'
  @returns 0 on OK, non-0 on PANIC
  """
  hosts = server_list
  assert [host, port] in server_list
  index = hosts.index([host, port])
  hl = map( lambda t: ':'.join(t), server_list)
  command = "python ~/server/main.py %s %s" % (index, " ".join(hl))
  remote_exec((host, 22), command)


def hard_reset():
  print 'Hard Reset on cluster'
  for host, port in server_list:
    take_server_down(host)
  for host, port in server_list:
    flush_iptables(host)
  for host, port in server_list:
    bring_server_up(host, port)
  sleep(RESET_DELAY)
    
