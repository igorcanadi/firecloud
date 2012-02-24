"""
Actuates commands in the test system


The 'host' variable is always some string that you can shove
into the sock's connect method to get get a connection.
"""


def partition(host1, port1, host2, port2):
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
  """
  pass


def partition_heal(host1, port1, host2, port2):
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
  """
  pass


def take_server_down(host, port):
  """ Takes the server down / kills the process / kills the VM.
  Implement this only if Swift says we need it
  @type host: str
  @param host: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port: int
  """
  pass


def bring_server_up(host, port):
  """ Undo-what ever take_server_down does, so that the server works again
  Implement this only if Swift says we need it
  @type host: str
  @param host: a string that is either the IP address or something that
  DNS can resolve to an IP adddress
  @type port: int
  """
  pass
