#!/usr/bin/env python

"""
Command and control for the servers
"""

from optparse import OptionParser
from os import chdir
from os.path import dirname, abspath

proxies_cfg = 'proxy.cfg'


PROXY = { }

def get_proxy(serv):
  """ Maps a (host, port) to a (host, port) to ssh/scp to
  """
  return (serv[0], 22)


def _remote_exec(gate, cmd):
  #retval = subprocess.call(command, shell=True)
  #if retval != 0:
  #    return retval
  print 'ssh -i keys/id_rsa -p {0[1]} user739@{0[0]} \"nohup {1} &\"'.format(gate, cmd)


def remote_exec(serv, cmd):
  _remote_exec(get_proxy(serv), cmd)


def start_servers(servs):
  """ Starts the servers:
  @type servs: list of (host, port)
  """
  argl = map(str, map(lambda t: ':'.join(t), servs))
  for i, srv in enumerate(servs):
    remote_exec(srv, './fresh_start.sh {0} {1}'.format(i, srv))


def deploy(serv):
  """ copy over files to the server
  @type servs: list of (host, port)
  """
  host, port = get_proxy(serv)
  print 'scp -i keys/id_rsa -P {port} -r * user739@{host}:~'.format(host=host, port=port)


if __name__ == '__main__':
  parser = OptionParser()
  (options, args) = parser.parse_args()
  options.deploy = True

  if len(args) == 0:
    print 'usage: {0} HOST:PORT ...'.format(__file__)

  servs = map(lambda s: s.split(':'), args)

  if options.deploy:
    chdir(dirname(abspath(__file__)))
    for serv in servs:
      deploy(serv)
  start_servers(servs)
