#!/usr/bin/env python

"""
Command and control for the servers
"""

from optparse import OptionParser
from os import chdir, system
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
  argl = ' '.join(map(str, map(lambda t: ':'.join(t), servs)))
  for i, srv in enumerate(servs):
    print 'Starting server:', srv
    remote_exec(srv, './startup.sh {0} {1}'.format(i, argl))


def deploy(serv):
  """ copy over files to the server
  @type servs: list of (host, port)
  """
  host, port = get_proxy(serv)
  system('scp -i keys/id_rsa -P {port} -r * user739@{host}:~'.format(host=host, port=port))


if __name__ == '__main__':
  parser = OptionParser()
  parser.add_option("-d", "--deploy",
                        action="store_true", dest="deploy", default=False,
                                          help="don't print status messages to stdout")
  (options, args) = parser.parse_args()

  if len(args) == 0:
    print 'usage: {0} HOST:PORT ...'.format(__file__)

  servs = map(lambda s: s.split(':'), args)

  if options.deploy:
    chdir(dirname(abspath(__file__)))
    for serv in servs:
      deploy(serv)
  start_servers(servs)
